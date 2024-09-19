from collections import OrderedDict

from api.serializers import GeopackageSerializer, ModelSerializer, StyleSerializer, LayerDefinitionSerializer, WavefrontSerializer
from base.license import zip_a_file_if_not_zipfile
from django.contrib.postgres.search import SearchVector
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import cache_page
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from drf_multiple_model.views import FlatMultipleModelAPIView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.views.generic import ListView, DetailView
from rest_framework_simplejwt.tokens import RefreshToken, api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import reverse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import time
from django.utils.translation import gettext_lazy as _
from api.forms import UserTokenForm
from django.contrib import messages

# models
from geopackages.models import Geopackage
from models.models import Model
from rest_framework import filters, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from styles.models import Style
from layerdefinitions.models import LayerDefinition
from wavefronts.models import Wavefront
from api.models import UserOutstandingToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

def filter_resource_type(queryset, request, *args, **kwargs):
    resource_type = request.query_params["resource_type"]
    if resource_type.lower() == "3dmodel":
        resource_type = "wavefront"
    if queryset.model.__name__.lower() == resource_type.lower():
        return queryset
    else:
        return queryset.none()


def filter_resource_subtype(queryset, request, *args, **kwargs):
    resource_subtype = request.query_params["resource_subtype"]
    if queryset.model.__name__ == "Style":
        return queryset.filter(style_type__name__iexact=resource_subtype)
    else:
        return queryset.none()


def filter_creator(queryset, request, *args, **kwargs):
    creator = request.query_params["creator"]
    qs = queryset.annotate(
        search=(
            SearchVector("creator__username")
            + SearchVector("creator__first_name")
            + SearchVector("creator__last_name")
        )
    ).filter(search=creator)
    return qs


def filter_keyword(queryset, request, *args, **kwargs):
    keyword = request.query_params["keyword"]
    qs = queryset.annotate(
        search=(SearchVector("name") + SearchVector("description"))
    ).filter(search=keyword)
    return qs


def filter_general(queryset, request, *args, **kwargs):
    resource_type = request.query_params.get("resource_type", None)
    resource_subtype = request.query_params.get("resource_subtype", None)
    creator = request.query_params.get("creator", None)
    keyword = request.query_params.get("keyword", None)
    if resource_type:
        queryset = filter_resource_type(queryset, request, *args, **kwargs)
    if resource_subtype:
        queryset = filter_resource_subtype(queryset, request, *args, **kwargs)
    if creator:
        queryset = filter_creator(queryset, request, *args, **kwargs)
    if keyword:
        queryset = filter_keyword(queryset, request, *args, **kwargs)
    return queryset


class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 10

    def format_response(self, data):
        """
        override the output of pagination
        """

        return OrderedDict(
            [
                ("total", self.total),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )


# cache for 2 hours
@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
class ResourceAPIList(FlatMultipleModelAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LimitPagination

    add_model_type = False

    filter_backends = (filters.SearchFilter,)
    search_field = ("name", "creator")

    querylist = [
        {
            "queryset": LayerDefinition.approved_objects.all(),
            "serializer_class": LayerDefinitionSerializer,
            "filter_fn": filter_general,
        },
        {
            "queryset": Wavefront.approved_objects.all(),
            "serializer_class": WavefrontSerializer,
            "filter_fn": filter_general,
        },
        {
            "queryset": Geopackage.approved_objects.all(),
            "serializer_class": GeopackageSerializer,
            "filter_fn": filter_general,
        },
        {
            "queryset": Model.approved_objects.all(),
            "serializer_class": ModelSerializer,
            "filter_fn": filter_general,
        },
        {
            "queryset": Style.approved_objects.all(),
            "serializer_class": StyleSerializer,
            "filter_fn": filter_general,
        },
    ]


class ResourceAPIDownload(APIView):
    """
    Download a resource in a zipfile.

    The zipfile only contains a resource file.
    """

    # Cache page for the requested url
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        if Geopackage.approved_objects.filter(uuid=uuid).exists():
            object = Geopackage.approved_objects.get(uuid=uuid)
        elif Model.approved_objects.filter(uuid=uuid).exists():
            object = Model.approved_objects.get(uuid=uuid)
        elif Style.approved_objects.filter(uuid=uuid).exists():
            object = Style.approved_objects.get(uuid=uuid)
        elif LayerDefinition.approved_objects.filter(uuid=uuid).exists():
            object = LayerDefinition.approved_objects.get(uuid=uuid)
        elif Wavefront.approved_objects.filter(uuid=uuid).exists():
            object = Wavefront.approved_objects.get(uuid=uuid)
        else:
            raise Http404

        object.increase_download_counter()
        object.save(update_fields=['download_count'])
        # zip the resource
        zipfile = zip_a_file_if_not_zipfile(object.file.file.name)

        response = HttpResponse(
            zipfile.getvalue(), content_type="application/x-zip-compressed"
        )
        response["Content-Disposition"] = "attachment; filename=%s.zip" % (
            slugify(object.name, allow_unicode=True)
        )
        return response


class UserTokenDetailView(DetailView):
    """
    Hub token detail
    """
    model = OutstandingToken
    queryset = OutstandingToken.objects.all()
    template_name = "user_token_detail.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(UserTokenDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserTokenDetailView, self).get_context_data(**kwargs)
        token_id = self.kwargs.get('pk')
        user_token = get_object_or_404(
            UserOutstandingToken, 
            pk=token_id,
            is_blacklisted=False,
            is_newly_created=True
        )
        outstanding_token = get_object_or_404(
            OutstandingToken, 
            pk=user_token.token.pk, 
            user=self.request.user
        )
        try:
            token = RefreshToken(outstanding_token.token)
            token['refresh_jti'] = token[api_settings.JTI_CLAIM]
        except (InvalidToken, TokenError) as e:
            context = {}
            self.template_name = "user_token_invalid_or_expired.html"
            return context
        timestamp_from_last_edit = int(time.time())        
        context.update(
            {
                "access_token": str(token.access_token),
                "object": user_token,
                'timestamp_from_last_edit': timestamp_from_last_edit
            }
        )
        user_token.is_newly_created = False
        user_token.save()
        return context


class UserTokenListView(ListView):
    """
    Hub token list
    """
    model = UserOutstandingToken
    queryset = UserOutstandingToken.objects.all().order_by("-token__created_at")
    template_name = "user_token_list.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(UserTokenListView, self).dispatch(*args, **kwargs)

    def get_filtered_queryset(self, qs):
        return qs.filter(
            is_blacklisted=False
        )

    def get_queryset(self):
        qs = super(UserTokenListView, self).get_queryset()
        qs = self.get_filtered_queryset(qs)
        return qs



@login_required
@transaction.atomic
def user_token_create(request):
    if request.method == "POST":
        user = request.user
        refresh = RefreshToken.for_user(user)
        jti = refresh[api_settings.JTI_CLAIM]
        outstanding_token = OutstandingToken.objects.get(jti=jti)
        user_token = UserOutstandingToken.objects.create(
            user=user,
            token=outstanding_token,
            is_blacklisted=False,
            is_newly_created=True
        )

        return HttpResponseRedirect(
            reverse("user_token_detail", args=[user_token.pk])
        )


@login_required
@transaction.atomic
def user_token_update(request, token_id):
    print(token_id)
    user_token = get_object_or_404(
        UserOutstandingToken, 
        pk=token_id,
        is_blacklisted=False
    )
    outstanding_token = get_object_or_404(
        OutstandingToken, 
        pk=user_token.token.pk, 
        user=request.user
    )
    if request.method == "POST":
        form = UserTokenForm(request.POST, instance=user_token)
        if form.is_valid():
            form.save()
            msg = _("The token description has been successfully updated.")
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(
                reverse("user_token_list")
            )
    else:
        form = UserTokenForm(instance=user_token)

    return render(
        request,
        "user_token_form.html",
        {"form": form, "token": user_token}
    )


@login_required
@transaction.atomic
def user_token_delete(request, token_id):
    user_token = get_object_or_404(
        UserOutstandingToken, 
        pk=token_id,
        is_blacklisted=False
    )
    outstanding_token = get_object_or_404(
        OutstandingToken, 
        pk=user_token.token.pk, 
        user=request.user
    )
    if "delete_confirm" in request.POST:
        try:
            token = RefreshToken(outstanding_token.token)
            token.blacklist()
            user_token.is_blacklisted = True
        except (InvalidToken, TokenError) as e:
            user_token.is_blacklisted = True
        user_token.save()

        msg = _("The token has been successfully deleted.")
        messages.success(request, msg, fail_silently=True)
        return HttpResponseRedirect(
            reverse("user_token_list")
        )
    return render(
        request,
        "user_token_delete.html",
        {"description": user_token.description, "username": outstanding_token.user},
    )

def _get_resource_serializer(resource_type):
    if resource_type.lower() == "geopackage":
        return GeopackageSerializer
    elif resource_type.lower() == "3dmodel":
        return WavefrontSerializer
    elif resource_type.lower() == "style":
        return StyleSerializer
    elif resource_type.lower() == "layerdefinition":
        return LayerDefinitionSerializer
    elif resource_type.lower() == "model":
        return ModelSerializer
    else:
        return None

def _get_resource_object(uuid, resource_type):
    if resource_type.lower() == "geopackage":
        return get_object_or_404(Geopackage.approved_objects, uuid=uuid)
    elif resource_type.lower() == "3dmodel":
        return get_object_or_404(Wavefront.approved_objects, uuid=uuid)
    elif resource_type.lower() == "style":
        return get_object_or_404(Style.approved_objects, uuid=uuid)
    elif resource_type.lower() == "layerdefinition":
        return get_object_or_404(LayerDefinition.approved_objects, uuid=uuid)
    elif resource_type.lower() == "model":
        return get_object_or_404(Model.approved_objects, uuid=uuid)
    else:
        return None

class ResourceCreateView(APIView):
    """
    Create a new Resource
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = _get_resource_serializer(request.data.get("resource_type"))(data=request.data)
        if serializer is None:
            return Response(
                {"resource_type": "Resource type not supported"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if serializer.is_valid():
            serializer.save(creator=request.user)
            if hasattr(serializer, 'new_filepath'):
                serializer.instance.file.name = serializer.new_filepath
                serializer.instance.save()
            if hasattr(serializer, 'style_type'):
                serializer.instance.style_type = serializer.style_type
                serializer.instance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResourceDetailView(APIView):
    """
    Retrieve or update a Resource
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        resource_type = kwargs.get("resource_type")
        object = _get_resource_object(uuid, resource_type)
        if object is None:
            raise Http404
        if not object.creator.is_staff and object.creator != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = _get_resource_serializer(resource_type)(object)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        resource_type = kwargs.get("resource_type")
        object = _get_resource_object(uuid, resource_type)
        if object is None:
            raise Http404
        if not object.creator.is_staff and object.creator != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = _get_resource_serializer(resource_type)(object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        resource_type = kwargs.get("resource_type")
        object = _get_resource_object(uuid, resource_type)
        if object is None:
            raise Http404
        if not object.creator.is_staff and object.creator != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)