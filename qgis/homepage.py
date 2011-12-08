from django.shortcuts import render_to_response
from django.template import RequestContext
from plugins.models import Plugin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from feedjack.models import Post


def homepage(request):
    """
    Renders the home page
    """
    fresh = Plugin.fresh_objects.all()[:5]
    featured = Plugin.featured_objects.all().exclude(pk__in=[p.pk for p in fresh])[:5]
    popular = Plugin.popular_objects.all().exclude(pk__in=[p.pk for p in fresh]).exclude(pk__in=[p.pk for p in featured])[:5]
    posts = Post.objects.all()[:5]
    try:
        content = FlatPage.objects.get(url='/').content
    except FlatPage.DoesNotExist:
        content = _('To add content here, create a FlatPage with url="/"')

    return render_to_response('flatpages/homepage.html', {
                'featured' : featured,
                'fresh' : fresh,
                'popular' : popular,
                'content' : content,
                'posts' : posts,
            }, context_instance=RequestContext(request))
