from django import template
from PIL import Image, UnidentifiedImageError
import xml.etree.ElementTree as ET

register = template.Library()


@register.filter("klass")
def klass(ob):
    return ob.__class__.__name__


@register.simple_tag(takes_context=True)
def plugin_title(context):
    """Returns plugin name for title"""
    title = ""

    if "title" in context:
        title = context["title"]
    if "plugin" in context:
        title = context["plugin"].name
    if "version" in context:
        title = "{plugin} {version}".format(
            plugin=context["version"].plugin.name, version=context["version"].version
        )
    if "page_title" in context:
        title = context["page_title"]
    return title

@register.filter
def file_extension(value):
    return value.split('.')[-1].lower()

@register.filter
def is_image_valid(image):
    if not image:
        return False
    # Check if the file is an SVG by extension
    if image.path.lower().endswith('.svg'):
        return _validate_svg(image.path)
    return _validate_image(image.path)


def _validate_svg(file_path):
    try:
        # Parse the SVG file to ensure it's well-formed XML
        ET.parse(file_path)
        return True
    except (ET.ParseError, FileNotFoundError):
        return False

def _validate_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except (FileNotFoundError, UnidentifiedImageError):
        return False

@register.filter
def feedbacks_not_completed(feedbacks):
    return feedbacks.filter(is_completed=False)
