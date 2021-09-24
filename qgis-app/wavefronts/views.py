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


from wavefronts.forms import UpdateForm, UploadForm
from wavefronts.models import Wavefront, Review


class ResourceMixin():
    """Mixin class for Wavefront."""

    model = Wavefront

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = 'Wavefront'

    # The url name in urls.py should start with this value
    resource_name_url_base = 'wavefront'


class WavefrontCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a Wavefront File"""

    form_class = UploadForm


class WavefrontDetailView(ResourceMixin, ResourceBaseDetailView):
    """Wavefront Detail View"""


class WavefrontUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update the Wavefront"""

    form_class = UpdateForm


class WavefrontListView(ResourceMixin, ResourceBaseListView):
    """Approved Wavefront ListView"""


class WavefrontUnapprovedListView(ResourceMixin,
                                   ResourceBaseUnapprovedListView):
    """Unapproved Wavefront ListView"""


class WavefrontRequireActionListView(ResourceMixin,
                                      ResourceBaseRequireActionListView):
    """Wavefront Requires Action"""


class WavefrontDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a Wavefront."""


class WavefrontReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class WavefrontDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a Wavefront"""


def wavefront_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
