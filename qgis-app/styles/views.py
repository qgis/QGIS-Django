from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from .models import Style


class StyleListView(ListView):
    model = Style
    context_object_name = 'style_list'


class StyleDetailView(DetailView):
    model = Style
    context_object_name = 'style_detail'
    template_name = 'styles/style_detail.html'
    slug_url_kwarg = 'name'
    slug_field = 'name'


def style_download(request, name):
    """
    Download style file and update download_count in Style model
    """
    style = get_object_or_404(Style, name=name)
    style.download_count += 1
    style.save()
    with open(style.xml_file.file.name, 'rb') as style_file:
        file_content = style_file.read()
        response = HttpResponse(file_content, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename=%s.xml' % (
            style.name
        )
        return response
