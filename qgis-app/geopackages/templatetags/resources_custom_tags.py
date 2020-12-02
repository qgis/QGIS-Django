from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def anchor_sort_arrow(name, order_by, current_order, current_query):
    """
    Returns html element: anchor arrow for sorting purpose
    """

    desc_current_order = False
    if current_order:
        order = current_order.split("-")
        if len(order) > 1:
            desc_current_order = True
            current_order = order[1]

    if order_by == current_order:
        class_arrow = "sorted"
    else:
        class_arrow = ""

    if not current_query:
        current_query = ''

    if not desc_current_order:
        result = (
            '%s <a href="?order_by=%s&&q=%s&&" class="%s">'
            '<i class="icon-arrow-up"></i></a>'
            '<a href="?order_by=-%s&&q=%s&&" class="">'
            '<i class="icon-arrow-down"></i></a>' % (
                name, order_by, current_query, class_arrow,
                order_by, current_query))
    else:
        result = (
            '%s <a href="?order_by=%s&&q=%s&&" class="">'
            '<i class="icon-arrow-up"></i></a>'
            '<a href="?order_by=-%s&&q=%s&&" class="%s">'
            '<i class="icon-arrow-down"></i></a>' % (
                name, order_by, current_query,
                order_by, current_query, class_arrow))
    return mark_safe(result)


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)