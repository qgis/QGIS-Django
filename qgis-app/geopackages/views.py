import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import (CreateView,
                                  DetailView,
                                  DeleteView,
                                  ListView,
                                  UpdateView,
                                  View)

from base.license import zipped_with_license
from base.views.processing_view import (ResourceBaseCreateView,
                                        ResourceBaseDetailView,
                                        ResourceBaseUpdateView,
                                        ResourceBaseListView,
                                        ResourceBaseUnapprovedListView,
                                        ResourceBaseRequireActionListView,
                                        ResourceBaseDeleteView,
                                        ResourceBaseReviewView,
                                        ResourceBaseDownload,
                                        resource_nav_content)

from geopackages.forms import (GeopackageReviewForm,
                               UpdateForm,
                               UploadForm,)
from geopackages.models import Geopackage, Review


class ResourceMixin():
    """Mixin class for Geopackage."""

    model = Geopackage

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = 'GeoPackage'

    # The url name in urls.py should start start with this value
    resource_name_url_base = 'geopackage'


class GeopackageCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a GeoPackage File"""

    form_class = UploadForm


class GeopackageDetailView(ResourceMixin, ResourceBaseDetailView):

    pass


class GeopackageUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update a GeoPackage"""

    form_class = UpdateForm


class GeopackageListView(ResourceMixin, ResourceBaseListView):
    pass


class GeopackageUnapprovedListView(ResourceMixin,
                                   ResourceBaseUnapprovedListView):
    pass


class GeopackageRequireActionListView(ResourceMixin,
                                      ResourceBaseRequireActionListView):
    """Geopackage Requires Action """


class GeopackageDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """
    Delete a GeoPackage.
    """

class GeopackageReviewView(ResourceMixin, ResourceBaseReviewView):
    pass


class GeopackageDownloadView(ResourceMixin, ResourceBaseDownload):
    pass


def geopackage_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response


