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
from base.views.processing_view import _, resource_notify, messages
from base.views.processing_view import HttpResponseRedirect, reverse_lazy

from layerdefinitions.file_handler import get_url_datasource, get_provider
from layerdefinitions.forms import (UpdateForm, UploadForm)
from layerdefinitions.models import LayerDefinition, Review


class ResourceMixin():
    """Mixin class for Geopackage."""

    model = LayerDefinition

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = 'Layer Definition'

    # The url name in urls.py should start start with this value
    resource_name_url_base = 'layerdefinition'


class LayerDefinitionCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a Layer Definition File (.qlr)."""

    form_class = UploadForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.url_datasource = get_url_datasource(obj.file.file)
        obj.provider = get_provider(obj.file.file)
        obj.save()
        resource_notify(obj, resource_type=self.resource_name)
        msg = _(self.success_message)
        messages.success(self.request, msg, 'success', fail_silently=True)
        return super(ResourceBaseCreateView, self).form_valid(form)


class LayerDefinitionDetailView(ResourceMixin, ResourceBaseDetailView):
    """Detail View"""

    license_template = 'base/includes/layerdefinition/license.html'
    css = ('css/detail_page.css',)

    def get_context_data(self, **kwargs):
        context = super(LayerDefinitionDetailView, self).get_context_data()
        context['is_qlr'] = True
        return context


class LayerDefinitionUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update View"""

    form_class = UpdateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.require_action = False
        obj.approved = False
        obj.url_datasource = get_url_datasource(obj.file.file)
        obj.provider = get_provider(obj.file.file)
        obj.save()
        resource_notify(obj, created=False, resource_type=self.resource_name)
        msg = _("The %s has been successfully updated." % self.resource_name)
        messages.success(self.request, msg, 'success', fail_silently=True)
        url_name = '%s_detail' % self.resource_name_url_base
        return HttpResponseRedirect(
            reverse_lazy(url_name, kwargs={'pk': obj.id}))


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
