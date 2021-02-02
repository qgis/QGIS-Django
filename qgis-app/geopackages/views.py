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

from geopackages.forms import (UpdateForm, UploadForm,)
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
    """Geopackage Detail View"""


class GeopackageUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update the GeoPackage"""

    form_class = UpdateForm


class GeopackageListView(ResourceMixin, ResourceBaseListView):
    """Approved GeoPackage ListView"""


class GeopackageUnapprovedListView(ResourceMixin,
                                   ResourceBaseUnapprovedListView):
    """Unapproved GeoPackage ListView"""


class GeopackageRequireActionListView(ResourceMixin,
                                      ResourceBaseRequireActionListView):
    """Geopackage Requires Action"""


class GeopackageDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a GeoPackage."""


class GeopackageReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class GeopackageDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a GeoPackage"""


def geopackage_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
