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

from models.forms import UpdateForm, UploadForm
from models.models import Model, Review


class ResourceMixin():
    """Mixin class for Model."""

    model = Model

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = 'Model'

    # The url name in urls.py should start with this value
    resource_name_url_base = 'model'


class ModelCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a Model File"""

    form_class = UploadForm


class ModelDetailView(ResourceMixin, ResourceBaseDetailView):
    """Model Detail View"""


class ModelUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update the Model"""

    form_class = UpdateForm


class ModelListView(ResourceMixin, ResourceBaseListView):
    """Approved Model ListView"""


class ModelUnapprovedListView(ResourceMixin,
                                   ResourceBaseUnapprovedListView):
    """Unapproved Model ListView"""


class ModelRequireActionListView(ResourceMixin,
                                      ResourceBaseRequireActionListView):
    """Model Requires Action"""


class ModelDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a Model."""


class ModelReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class ModelDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a Model"""


def model_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
