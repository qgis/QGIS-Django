from django import template
register = template.Library()

@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__


@register.simple_tag(takes_context=True)
def plugin_title(context):
    """Returns plugin name for title"""
    title = ''
    if 'plugin' in context:
        title = context['plugin'].name
    if 'version' in context:
        title = '{plugin} {version}'.format(
            plugin=context['version'].plugin.name,
            version=context['version'].version
        )
    return title
