"""
ABP: patched version of django-taggit-templatetags to deal with
unpublished plugins: returns only approved_objects

"""

from django import template
from django.db import models
from django.db.models import Count
from django.core.exceptions import FieldError

from templatetag_sugar.register import tag
from templatetag_sugar.parser import Name, Variable, Constant, Optional, Model

from taggit import VERSION as TAGGIT_VERSION
from taggit.managers import TaggableManager
from taggit.models import TaggedItem, Tag
from taggit_templatetags import settings

from plugins.models import Plugin

from django.conf import settings as django_settings

TAGCLOUD_COUNT_GTE = getattr(django_settings, 'TAGCLOUD_COUNT_GTE', None)
T_MAX = getattr(settings, 'TAGCLOUD_MAX', 6.0)
T_MIN = getattr(settings, 'TAGCLOUD_MIN', 1.0)

register = template.Library()

def get_queryset():
    applabel = 'plugins'
    model = 'plugin'
    # filter tagged items
    queryset = TaggedItem.objects.filter(content_type__app_label=applabel.lower())
    queryset = queryset.filter(content_type__model=model.lower(), object_id__in = Plugin.approved_objects.values_list('id', flat=True))

    # get tags
    tag_ids = queryset.values_list('tag_id', flat=True)
    queryset = Tag.objects.filter(id__in=tag_ids)

    # Retain compatibility with older versions of Django taggit
    # a version check (for example taggit.VERSION <= (0,8,0)) does NOT
    # work because of the version (0,8,0) of the current dev version of django-taggit
    try:
        qs = queryset.annotate(num_times=Count('taggeditem_items'))
    except FieldError:
        qs = queryset.annotate(num_times=Count('taggit_taggeditem_items'))
    if TAGCLOUD_COUNT_GTE:
        qs = qs.filter(num_times__gte=TAGCLOUD_COUNT_GTE)
    return qs

def get_weight_fun(t_min, t_max, f_min, f_max):
    def weight_fun(f_i, t_min=t_min, t_max=t_max, f_min=f_min, f_max=f_max):
        # Prevent a division by zero here, found to occur under some
        # pathological but nevertheless actually occurring circumstances.
        if f_max == f_min:
            mult_fac = 1.0
        else:
            mult_fac = float(t_max-t_min)/float(f_max-f_min)

        return t_max - (f_max-f_i)*mult_fac
    return weight_fun

@tag(register, [Constant('as'), Name()])
def get_plugins_taglist(context, asvar):
    queryset = get_queryset()
    queryset = queryset.order_by('-num_times')
    context[asvar] = queryset
    return ''

@tag(register, [Constant('as'), Name()])
def get_plugins_tagcloud(context, asvar):
    queryset = get_queryset()
    num_times = queryset.values_list('num_times', flat=True)
    if (len(num_times) == 0):
        context[asvar] = queryset
        return ''
    weight_fun = get_weight_fun(T_MIN, T_MAX, min(num_times), max(num_times))
    queryset = queryset.order_by('name')
    for tag in queryset:
        tag.weight = weight_fun(tag.num_times)
    context[asvar] = queryset
    return ''

def include_plugins_tagcloud(forvar=None):
    pass

def include_plugins_taglist(forvar=None):
    pass


register.inclusion_tag('plugins/plugins_taglist_include.html')(include_plugins_taglist)
register.inclusion_tag('plugins/plugins_tagcloud_include.html')(include_plugins_tagcloud)
