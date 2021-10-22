import os
from zipfile import ZipFile
from django.http import Http404, HttpResponse

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

from wavefronts.utilities import get_obj_info


class ResourceMixin():
    """Mixin class for Wavefront."""

    model = Wavefront

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = '3D Model'

    # The url name in urls.py should start with this value
    resource_name_url_base = 'wavefront'


class WavefrontCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a Wavefront File"""

    form_class = UploadForm
    is_1mb_limit_enable = False


class WavefrontDetailView(ResourceMixin, ResourceBaseDetailView):
    """Wavefront Detail View"""

    is_3d_model = True
    js = ({'src': 'wavefront/js/test.js'},)
    css = ('wavefront/css/wavefront.css',)


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


class WavefrontDetailWithViewerView(WavefrontDetailView):

    def get_template_names(self):
        return 'wavefronts/viewer.html'


def wavefront_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response


def wavefront_obj_file(request, pk):
    try:
        wavefront = Wavefront.objects.get(pk=pk)
        file = wavefront.file
    except Wavefront.DoesNotExist:
        raise Http404('Wavefront does not exist')
    obj_filename, obj_filesize = get_obj_info(file)
    path, filename = os.path.split(obj_filename)
    obj_data = ZipFile(file).read(obj_filename)
    response = HttpResponse(obj_data, content_type='model/obj')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
