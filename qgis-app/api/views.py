from collections import OrderedDict

from api.serializers import GeopackageSerializer, ModelSerializer, StyleSerializer
from base.license import zip_a_file_if_not_zipfile
from django.contrib.postgres.search import SearchVector
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import cache_page
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from drf_multiple_model.views import FlatMultipleModelAPIView

# models
from geopackages.models import Geopackage
from models.models import Model
from rest_framework import filters, permissions
from rest_framework.views import APIView
from styles.models import Style


def filter_resource_type(queryset, request, *args, **kwargs):
    resource_type = request.query_params["resource_type"]
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
