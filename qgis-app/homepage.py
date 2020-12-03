from django.shortcuts import render
from django.template import RequestContext
from plugins.models import Plugin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
#from feedjack.models import Post


def homepage(request):
    """
    Renders the home page
    """
    latest = Plugin.latest_objects.all()[:10]
    featured = Plugin.featured_objects.all()[:10]
    popular = Plugin.popular_objects.all()[:10]
    try:
        content = FlatPage.objects.get(url='/').content
    except FlatPage.DoesNotExist:
        content = _('To add content here, create a FlatPage with url="/"')

    return render(request, 'flatpages/homepage.html', {
                'featured' : featured,
                'latest' : latest,
                'popular' : popular,
                'content' : content,
            })

