import django.utils.copycompat as copy
from django.forms.widgets import Textarea
from django.template.loader import render_to_string
from django.utils import simplejson
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe

from olwidget import utils

# Default settings for paths and API URLs.  These can all be overridden by
# specifying a value in settings.py

setattr(settings, "OLWIDGET_MEDIA_URL", 
    getattr(settings, 
        "OLWIDGET_MEDIA_URL", 
        utils.url_join(settings.MEDIA_URL, "olwidget")))

api_defaults = {
    'GOOGLE_API_KEY': "",
    'YAHOO_APP_ID': "",
    'CLOUDMADE_API_KEY': "",
    'GOOGLE_API': "http://maps.google.com/maps?file=api&v=2",
    'YAHOO_API': "http://api.maps.yahoo.com/ajaxymap?v=3.0",
    'OSM_API': "http://openstreetmap.org/openlayers/OpenStreetMap.js",
    'OL_API': "http://openlayers.org/api/2.9/OpenLayers.js",
    'MS_VE_API' : "http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6.1",
    'CLOUDMADE_API': utils.url_join(settings.OLWIDGET_MEDIA_URL, "js/cloudmade.js"),
    'OLWIDGET_JS': utils.url_join(settings.OLWIDGET_MEDIA_URL, "js/olwidget.js"),
    'OLWIDGET_CSS': utils.url_join(settings.OLWIDGET_MEDIA_URL, "css/olwidget.css"),
}

for key, default in api_defaults.iteritems():
    if not hasattr(settings, key):
        setattr(settings, key, default)


#
# Map widget
#

class Map(forms.Widget):
    """
    ``Map`` is a container widget for layers.  The constructor takes a list of
    vector layer instances, a dictionary of options for the map, a template
    to customize rendering, and a list of names for the layer fields.
    """

    default_template = 'olwidget/multi_layer_map.html'

    def __init__(self, vector_layers=None, options=None, template=None,
            layer_names=None):
        self.vector_layers = VectorLayerList()
        for layer in vector_layers:
            self.vector_layers.append(layer)
        self.layer_names = layer_names
        self.options = options or {}
        # Though this layer is the olwidget.js default, it must be explicitly
        # set so {{ form.media }} knows to include osm.
        self.options['layers'] = self.options.get('layers', ['osm.mapnik'])
        self.template = template or self.default_template
        super(Map, self).__init__()

    def render(self, name, value, attrs=None):
        if value is None:
            values = [None for i in range(len(self.vector_layers))]
        elif not isinstance(value, (list, tuple)):
            values = [value]
        else:
            values = value
        attrs = attrs or {}
        # Get an arbitrary unique ID if we weren't handed one (e.g. widget used
        # outside of a form).
        map_id = attrs.get('id', "id_%s" % id(self))

        layer_js = []
        layer_html = []
        layer_names = self._get_layer_names(name)
        value_count = 0
        for i, layer in enumerate(self.vector_layers):
            if layer.editable:
                value = values[value_count]
                value_count += 1
            else:
                value = None
            lyr_name = layer_names[i]
            id_ = "%s_%s" % (map_id, lyr_name)
            # Use "prepare" rather than "render" to get both js and html
            (js, html) = layer.prepare(lyr_name, value, attrs={'id': id_ })
            layer_js.append(js)
            layer_html.append(html)

        attrs = attrs or {}
        context = {
            'id': map_id,
            'layer_js': layer_js,
            'layer_html': layer_html,
            'map_opts': simplejson.dumps(utils.translate_options(self.options)),
        }
        return render_to_string(self.template, context)

    def value_from_datadict(self, data, files, name):
        """ Return an array of all layers' values. """
        return [vl.value_from_datadict(data, files, lyr_name) for vl, lyr_name in zip(self.vector_layers, self._get_layer_names(name))]

    def _get_layer_names(self, name):
        """ 
        If the user gave us a layer_names parameter, use that.  Otherwise,
        construct names based on ``name``. 
        """
        n = len(self.vector_layers)
        if self.layer_names and len(self.layer_names) == n:
            return self.layer_names

        singleton = len(self.vector_layers.editable) == 1
        self.layer_names = []
        for i,layer in enumerate(self.vector_layers):
            if singleton and layer.editable:
                self.layer_names.append("%s" % name)
            else:
                self.layer_names.append("%s_%i" % (name, i))
        return self.layer_names

    def _has_changed(self, initial, data):
        if (initial is None) or (not isinstance(initial, (tuple, list))):
            initial = [u''] * len(data)
        for widget, initial, data in zip(self.vector_layers, initial, data):
            if widget._has_changed(initial, data):
                return True
        return False

    def _media(self):
        js = set()
        # collect scripts necessary for various base layers
        for layer in self.options['layers']:
            if layer.startswith("osm."):
                js.add(settings.OSM_API)
            elif layer.startswith("google."):
                js.add(settings.GOOGLE_API + "&key=%s" % settings.GOOGLE_API_KEY)
            elif layer.startswith("yahoo."):
                js.add(settings.YAHOO_API + "&appid=%s" % settings.YAHOO_APP_ID)
            elif layer.startswith("ve."):
                js.add(settings.MS_VE_API)
            elif layer.startswith("cloudmade."):
                js.add(settings.CLOUDMADE_API + "#" + settings.CLOUDMADE_API_KEY)
        js = [settings.OL_API, settings.OLWIDGET_JS] + list(js)
        return forms.Media(css={'all': (settings.OLWIDGET_CSS,)}, js=js)
    media = property(_media)

    def __unicode__(self):
        return self.render(None, None)

    def __deepcopy__(self, memo):
        obj = super(Map, self).__deepcopy__(memo)
        obj.vector_layers = copy.deepcopy(self.vector_layers)
        return obj

class VectorLayerList(list):
    def __init__(self, *args, **kwargs):
        super(VectorLayerList, self).__init__(*args, **kwargs)
        self.editable = []

    def append(self, obj):
        super(VectorLayerList, self).append(obj)
        if getattr(obj, "editable", False):
            self.editable.append(obj)

    def remove(self, obj):
        super(VectorLayerList, self).remove(obj)
        if getattr(obj, "editable", False):
            self.editable.remove(obj)

    def __deepcopy__(self, memo):
        obj = VectorLayerList()
        for thing in self:
            obj.append(copy.deepcopy(thing))
        return obj

#
# Layer widgets
#

class BaseVectorLayer(forms.Widget):
    editable = False
    def prepare(self, name, value, attrs=None):
        """
        Given the name, value and attrs, prepare both html and javascript
        components to handle this layer.  Should return (javascript, html)
        tuple.
        """
        raise NotImplementedError

    def render(self, name, value, attrs=None):
        """
        Return just the javascript component of this widget.  To also get the
        HTML component, call ``prepare``.
        """
        (javascript, html) = self.prepare(name, value, attrs)
        return javascript

    def __unicode__(self):
        return self.render(None, None)

class InfoLayer(BaseVectorLayer):
    """
    A wrapper for the javscript olwidget.InfoLayer() type.  Takes an an array
    [geometry, html] pairs, where the html will be the contents of a popup
    displayed over the geometry, and an optional options dict.  Intended for
    use as a sub-widget for a ``Map`` widget.
    """
    default_template = 'olwidget/info_layer.html'

    def __init__(self, info=None, options=None, template=None):
        self.info = info or []
        self.options = options or {}
        self.template = template or self.default_template
        super(InfoLayer, self).__init__()

    def prepare(self, name, value, attrs=None):
        wkt_array = []
        for geom, attr in self.info:
            wkt = utils.get_ewkt(geom)
            if isinstance(attr, dict):
                wkt_array.append([wkt, utils.translate_options(attr)])
            else:
                wkt_array.append([wkt, attr])
        info_json = simplejson.dumps(wkt_array)

        if name and not self.options.has_key('name'):
            self.options['name'] = forms.forms.pretty_name(name)

        context = {
            'info_array': info_json,
            'options': simplejson.dumps(utils.translate_options(self.options)),
        }
        js = mark_safe(render_to_string(self.template, context))
        html = ""
        return (js, html)

class EditableLayer(BaseVectorLayer):
    """
    A wrapper for the javascript olwidget.EditableLayer() type.  Intended for
    use as a sub-widget for the Map widget.
    """
    default_template = "olwidget/editable_layer.html"
    editable = True

    def __init__(self, options=None, template=None):
        self.options = options or {}
        self.template = template or self.default_template
        super(EditableLayer, self).__init__()

    def prepare(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        if name and not self.options.has_key('name'):
            self.options['name'] = forms.forms.pretty_name(name)
        attrs['id'] = attrs.get('id', "id_%s" % id(self))

        wkt = utils.get_ewkt(value)
        context = {
            'id': attrs['id'],
            'options': simplejson.dumps(utils.translate_options(self.options)),
        }
        js = mark_safe(render_to_string(self.template, context))
        html = mark_safe(forms.Textarea().render(name, wkt, attrs))
        return (js, html)

#
# Convenience single layer widgets for use in non-MapField fields.
#

class BaseSingleLayerMap(Map):
    """
    Base type for single-layer maps, for convenience and backwards
    compatibility.
    """
    def value_from_datadict(self, data, files, name):
        val = super(BaseSingleLayerMap, self).value_from_datadict(
                data, files, name)
        return val[0]

class EditableMap(BaseSingleLayerMap):
    """
    Convenience Map widget with a single editable layer.  Usage:

        forms.CharField(widget=EditableMap(options={}))

    """
    def __init__(self, options=None, **kwargs):
        super(EditableMap, self).__init__([EditableLayer()], options, **kwargs)
        
class InfoMap(BaseSingleLayerMap):
    """
    Convenience Map widget with a single info layer.
    """
    def __init__(self, info, options=None, **kwargs):
        super(InfoMap, self).__init__([InfoLayer(info)], options, **kwargs)

class MapDisplay(EditableMap):
    """
    Convenience Map widget for a single non-editable layer, with no popups.
    """
    def __init__(self, fields=None, options=None, **kwargs):
        options = options or {}
        options['editable'] = False
        super(MapDisplay, self).__init__(options, **kwargs)
        if fields:
            self.wkt = utils.collection_ewkt(fields)
        else:
            self.wkt = ""

    def __unicode__(self):
        return self.render(None, [self.wkt])

