import json

from base.views.processing_view import (
    ResourceBaseCreateView,
    ResourceBaseDeleteView,
    ResourceBaseDetailView,
    ResourceBaseDownload,
    ResourceBaseListView,
    ResourceBaseRequireActionListView,
    ResourceBaseReviewView,
    ResourceBaseUnapprovedListView,
    ResourceBaseUpdateView,
    resource_nav_content,
    resource_notify,
)
from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from styles.file_handler import read_xml_style
from styles.forms import UpdateForm, UploadForm
from styles.models import Review, Style, StyleType


class ResourceMixin:
    """Mixin class for Geopackage."""

    model = Style

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = "Style"

    # The url name in urls.py should start start with this value
    resource_name_url_base = "style"


class StyleCreateView(ResourceMixin, ResourceBaseCreateView):
    """
    Create a new style
    """

    form_class = UploadForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        xml_parse = read_xml_style(obj.file)
        if xml_parse:
            # check if name exists
            name_exist = Style.objects.filter(name__iexact=xml_parse["name"]).exists()
            if name_exist:
                obj.name = "%s_%s" % (
                    xml_parse["name"].title(),
                    get_random_string(length=5),
                )
            else:
                obj.name = xml_parse["name"].title()
            style_type = StyleType.objects.filter(symbol_type=xml_parse["type"]).first()
            if not style_type:
                style_type = StyleType.objects.create(
                    symbol_type=xml_parse["type"],
                    name=xml_parse["type"].title(),
                    description="Automatically created from '"
                    "'an uploaded Style file",
                )
            obj.style_type = style_type
        obj.save()
        resource_notify(obj, self.resource_name)
        msg = _("The Style has been successfully created.")
        messages.success(self.request, msg, "success", fail_silently=True)
        return HttpResponseRedirect(reverse("style_detail", kwargs={"pk": obj.id}))


class StyleDetailView(ResourceMixin, ResourceBaseDetailView):
    """Style Detail View"""


class StyleUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """
    Update a style
    """

    form_class = UpdateForm

    def form_valid(self, form):
        """
        Update the style type according to the style XML file.
        """

        obj = form.save(commit=False)
        xml_parse = read_xml_style(obj.file)
        if xml_parse:
            obj.style_type = StyleType.objects.filter(
                symbol_type=xml_parse["type"]
            ).first()
        obj.require_action = False
        obj.save()
        resource_notify(obj, created=False, resource_type=self.resource_name)
        msg = _("The Style has been successfully updated.")
        messages.success(self.request, msg, "success", fail_silently=True)
        return HttpResponseRedirect(reverse_lazy("style_detail", kwargs={"pk": obj.id}))


class StyleListView(ResourceMixin, ResourceBaseListView):
    """Style ListView."""


class StyleByTypeListView(StyleListView):
    """Display StyleListView filtered on style type"""

    def get_queryset(self):
        qs = super().get_queryset()
        style_type = self.kwargs["style_type"]
        return qs.filter(style_type__name=style_type)

    def get_context_data(self, **kwargs):
        """
        Override get_context_data.

        Add 'title' to be displayed as page title
        """

        context = super(StyleByTypeListView, self).get_context_data(**kwargs)
        context["title"] = "%s Styles" % (self.kwargs["style_type"],)
        return context


class StyleUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
    """Unapproved Style ListView."""


class StyleRequireActionListView(ResourceMixin, ResourceBaseRequireActionListView):
    """Style requires action."""


class StyleDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a style."""


class StyleReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class StyleDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a style"""


def style_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response


@never_cache
def style_type_list(request):
    media_path = getattr(settings, "MEDIA_URL")
    qs = StyleType.objects.all()
    qs_json = serializers.serialize("json", qs)
    qs_load = json.loads(qs_json)
    qs_add = {"qs": qs_load, "icon_url": media_path}
    qs_json = json.dumps(qs_add)
    return HttpResponse(qs_json, content_type="application/json")
