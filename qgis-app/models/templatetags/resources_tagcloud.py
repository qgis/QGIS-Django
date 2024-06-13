"""
ABP: patched version of django-taggit-templatetags to deal with
unpublished resources: returns only approved_objects
"""

from django import template
from django.conf import settings as django_settings
from django.core.exceptions import FieldError
from django.db.models import Count
from taggit.models import Tag, TaggedItem
from taggit_templatetags import settings
from django.apps import apps

TAGCLOUD_COUNT_GTE = getattr(django_settings, "TAGCLOUD_COUNT_GTE", None)
T_MAX = getattr(settings, "TAGCLOUD_MAX", 6.0)
T_MIN = getattr(settings, "TAGCLOUD_MIN", 1.0)

register = template.Library()

def get_queryset(app_label, model):
    # Get model class
    model_class = apps.get_model(app_label, model)
    # Filter tagged items based on approved objects
    queryset = TaggedItem.objects.filter(
        content_type__app_label=app_label.lower(),
        content_type__model=model.lower(),
        object_id__in=model_class.approved_objects.values_list("id", flat=True),
    )
    # Get tag IDs
    tag_ids = queryset.values_list("tag_id", flat=True)
    # Filter tags
    queryset = Tag.objects.filter(id__in=tag_ids)

    # Annotate with count of tagged items
    try:
        queryset = queryset.annotate(num_times=Count("taggeditem_items"))
    except FieldError:
        queryset = queryset.annotate(num_times=Count("taggit_taggeditem_items"))

    # Show only the tags that are used over a given times (defined by TAGCLOUD_COUNT_GTE)
    if TAGCLOUD_COUNT_GTE:
        queryset = queryset.filter(num_times__gte=TAGCLOUD_COUNT_GTE)

    return queryset

def get_weight_fun(t_min, t_max, f_min, f_max):
    def weight_fun(f_i, t_min=t_min, t_max=t_max, f_min=f_min, f_max=f_max):
        if f_max == f_min:
            mult_fac = 1.0
        else:
            mult_fac = float(t_max - t_min) / float(f_max - f_min)
        return t_max - (f_max - f_i) * mult_fac
    return weight_fun

@register.simple_tag(takes_context=True)
def get_resources_tagcloud(context, app_label, model):
    queryset = get_queryset(app_label, model)
    num_times = queryset.values_list("num_times", flat=True)

    if not num_times:
        return queryset

    weight_fun = get_weight_fun(T_MIN, T_MAX, min(num_times), max(num_times))
    queryset = queryset.order_by("name")
    for tag in queryset:
        tag.weight = weight_fun(tag.num_times)

    return queryset

@register.inclusion_tag("base/includes/resources_tagcloud_modal_include.html", takes_context=True)
def include_resources_tagcloud_modal(context, app_label, model):
    tags = get_resources_tagcloud(context, app_label, model)
    tags_title = model[0].upper() + model[1:]
    if str(model).lower() == "wavefront":
        tags_title = "3D Model"
    elif str(model).lower() == "layerdefinition":
        tags_title = "Layer Definition"

    return {
        'tags': tags, 
        'tags_title': tags_title + " Tags",
        'tags_list_url': model + "_tag"
    }
