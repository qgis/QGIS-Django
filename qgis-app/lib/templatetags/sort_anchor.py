"""Modified by elpaso to work with django-sortable-listview"""
from django import template
from django.conf import settings
from django.template import Library

DEFAULT_SORT_UP = getattr(settings, "DEFAULT_SORT_UP", "&uarr;")
DEFAULT_SORT_DOWN = getattr(settings, "DEFAULT_SORT_DOWN", "&darr;")


register = template.Library()


sort_directions = {
    "asc": {"icon": DEFAULT_SORT_UP, "inverse": "desc"},
    "desc": {"icon": DEFAULT_SORT_DOWN, "inverse": "asc"},
    "": {"icon": DEFAULT_SORT_DOWN, "inverse": "asc"},
}


@register.tag
def anchor(parser, token):
    """
    Parses a tag that's supposed to be in this format: {% anchor field title %}
    """
    bits = [b.strip("\"'") for b in token.split_contents()]
    if len(bits) < 2:
        raise template.TemplateSyntaxError("anchor tag takes at least 1 argument")
    try:
        title = bits[2]
    except IndexError:
        title = bits[1].capitalize()
    return SortAnchorNode(bits[1].strip(), title.strip())


class SortAnchorNode(template.Node):
    """
    Renders an <a> HTML tag with a link which href attribute
    includes the field on which we sort and the direction.
    and adds an up or down arrow if the field is the one
    currently being sorted on.
    Eg.
        {% anchor name Name %} generates
        <a href="/the/current/path/?sort=name" title="Name">Name</a>
    """

    def __init__(self, field, title):
        self.field = field
        self.title = title

    def render(self, context):
        request = context["request"]
        getvars = request.GET.copy()

        if "sort" in getvars:
            sortby = getvars["sort"]
            del getvars["sort"]
        else:
            sortby = ""

        if sortby.startswith("-"):
            sortdir = "desc"
            sortby = sortby[1:]
        else:
            sortdir = "asc"

        # Invert
        if sortby == self.field:
            icon = sort_directions[sortdir]["icon"]
            sortdir = sort_directions[sortdir]["inverse"]
        else:
            icon = ""
        if len(getvars.keys()) > 0:
            urlappend = "&%s" % getvars.urlencode()
        else:
            urlappend = ""
        if icon:
            title = "%s %s" % (self.title, icon)
        else:
            title = self.title

        valid_fields = getattr(request, "valid_fields", [])
        valid_fields.append(self.field)
        setattr(request, "valid_fields", valid_fields)

        # Inverse?
        if sortby == self.field and sortdir == "desc":
            field = "-%s" % self.field
        else:
            field = self.field
        url = "%s?sort=%s%s" % (request.path, field, urlappend)
        return '<a href="%s" title="%s">%s</a>' % (url, self.title, title)
