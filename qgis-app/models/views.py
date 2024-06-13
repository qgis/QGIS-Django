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
)
from models.forms import UpdateForm, UploadForm
from models.models import Model, Review
from django.utils.translation import gettext_lazy as _
from urllib.parse import unquote


class ResourceMixin:
    """Mixin class for Model."""

    model = Model

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = "Model"

    # The url name in urls.py should start with this value
    resource_name_url_base = "model"


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


class ModelUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
    """Unapproved Model ListView"""


class ModelRequireActionListView(ResourceMixin, ResourceBaseRequireActionListView):
    """Model Requires Action"""


class ModelDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a Model."""


class ModelReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class ModelDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a Model"""


class ModelByTagView(ModelListView):
    """Display ModelListView filtered on model tag"""

    def get_filtered_queryset(self, qs):
        response = qs.filter(tagged_items__tag__slug=unquote(self.kwargs["model_tag"]))
        return response

    def get_queryset(self):
        qs = super().get_queryset()
        return self.get_filtered_queryset(qs)

    def get_context_data(self, **kwargs):
        context = super(ModelByTagView, self).get_context_data(**kwargs)
        context.update(
            {
                "title": _("Model tagged with: %s") % unquote(self.kwargs["model_tag"]),
                "page_title": _("Tag: %s") % unquote(self.kwargs["model_tag"])
            }
        )
        return context

def model_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
