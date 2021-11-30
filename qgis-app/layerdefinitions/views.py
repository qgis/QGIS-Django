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
from base.views.processing_view import (
    get_object_or_404, check_resources_access, TemplateResponse,
    HttpResponse, slugify
)

from layerdefinitions.file_handler import get_url_datasource, get_provider
from layerdefinitions.forms import (UpdateForm, UploadForm)
from layerdefinitions.models import LayerDefinition, Review
from layerdefinitions.license import zipped_with_license


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
    is_custom_license_agreement = True

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
    is_custom_license_agreement = True

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

    def get(self, request, *args, **kwargs):
        object = get_object_or_404(self.model, pk=self.kwargs['pk'])
        if not object.approved:
            if not check_resources_access(self.request.user, object):
                context = super(ResourceBaseDownload, self).get_context_data()
                context['object_name'] = object.name
                context['context'] = ('Download failed. This %s is '
                                      'not approved' % self.resource_name)
                return TemplateResponse(request, self.template_name, context)
        else:
            object.increase_download_counter()
            object.save()

        # zip the resource and license.txt
        zipfile = zipped_with_license(
            file=object.file.file.name,
            zip_subdir=object.name,
            custom_license=object.license
        )

        response = HttpResponse(
            zipfile.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % (
            slugify(object.name, allow_unicode=True)
        )
        return response


def layerdefinition_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
