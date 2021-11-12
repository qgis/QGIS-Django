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

from layerdefinitions.forms import (UpdateForm, UploadForm,)
from layerdefinitions.models import LayerDefinition, Review


class ResourceMixin():
    """Mixin class for Geopackage."""

    model = LayerDefinition

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = 'Layer Definition File'

    # The url name in urls.py should start start with this value
    resource_name_url_base = 'layerdefinition'


class LayerDefinitionCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a Layer Definition File (.qlr)."""

    form_class = UploadForm


class LayerDefinitionDetailView(ResourceMixin, ResourceBaseDetailView):
    """Detail View"""


class LayerDefinitionUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update View"""

    form_class = UpdateForm


class LayerDefinitionListView(ResourceMixin, ResourceBaseListView):
    """Approved Layer Definition File (.qlr) ListView"""


class LayerDefinitionUnapprovedListView(ResourceMixin,
                                        ResourceBaseUnapprovedListView):
    """Unapproved Layer Definition File (.qlr) ListView"""


class LayerDefinitionRequireActionListView(ResourceMixin,
                                           ResourceBaseRequireActionListView):
    """Layer Definition File (.qlr) Requires Action"""


class LayerDefinitionDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a Layer Definition File (.qlr)."""


class LayerDefinitionReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review."""


class LayerDefinitionDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a Layer Definition File (.qlr)."""


def layerdefinition_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
