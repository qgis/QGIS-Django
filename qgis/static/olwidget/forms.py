from django import forms
from django.contrib.gis.forms.fields import GeometryField

from olwidget.widgets import Map, BaseVectorLayer, EditableLayer
from olwidget.fields import MapField
from olwidget import utils

__all__ = ('MapModelForm', )

class BaseMapModelForm(forms.models.BaseModelForm):
    """
    ModelForm type that uses olwidget maps for geometry fields.  Multiple
    fields can be edited in a single map -- to do this, specify a property
    "maps" of the inner Meta class which lists fields and map options:

    class MyMapModelForm(MapModelForm):
        class Meta:
            model = MyModel
            maps = (
                (('geom1', 'geom2'), {'layers': ['google.streets]}), 
                (('geom3',), None), 
                ...
            ) 
    """
    def __init__(self, *args, **kwargs):
        super(BaseMapModelForm, self).__init__(*args, **kwargs)
        fix_initial_data(self.initial, self.initial_data_keymap)

    def clean(self):
        super(BaseMapModelForm, self).clean()
        fix_cleaned_data(self.cleaned_data, self.initial_data_keymap)
        return self.cleaned_data

class MapModelFormOptions(forms.models.ModelFormOptions):
    def __init__(self, options=None):
        super(MapModelFormOptions, self).__init__(options)
        self.maps = getattr(options, 'maps', None)


class MapModelFormMetaclass(type):
    """ 
    Metaclass for map-containing ModelForm widgets.  The implementation is
    mostly copied from django's ModelFormMetaclass, but we change the
    hard-coded parent class name and add our map field processing parts.
    """
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback',
                lambda f, **kwargs: f.formfield(**kwargs))
        try:
            parents = [b for b in bases if issubclass(b, MapModelForm)]
        except NameError:
            # We are defining MapModelForm itself.
            parents = None
        declared_fields = forms.models.get_declared_fields(bases, attrs, False)
        new_class = super(MapModelFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = forms.widgets.media_property(new_class)
        opts = new_class._meta = MapModelFormOptions(
                getattr(new_class, 'Meta', None))
        if opts.model:
            # If a model is defined, extract form fields from it.
            fields = forms.models.fields_for_model(opts.model, opts.fields,
                                      opts.exclude, opts.widgets, 
                                      formfield_callback)

            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields

        # Transform base fields by extracting types mentioned in 'maps'
        initial_data_keymap = apply_maps_to_modelform_fields(fields, opts.maps)

        new_class.initial_data_keymap = initial_data_keymap
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class

class MapModelForm(BaseMapModelForm):
    __metaclass__ = MapModelFormMetaclass

def fix_initial_data(initial, initial_data_keymap):
    """ 
    Take a dict like this as `initial`:
    { 'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
    and a dict like this as `initial_data_keymap`:
    { 'newkey1': ['key1', 'key2'], 'newkey2': ['key3']}
    and remap the initial dict to have this form:
    { 'newkey1': ['val1', 'val2'], 'newkey2': ['val3']}

    Used for rearranging initial data in fields to match declared maps.
    """
    if initial:
        for dest, sources in initial_data_keymap.iteritems():
            data = [initial.pop(s, None) for s in sources]
            initial[dest] = data
    return initial

def fix_cleaned_data(cleaned_data, initial_data_keymap):
    for group, keys in initial_data_keymap.iteritems():
        if cleaned_data.has_key(group):
            vals = cleaned_data.pop(group)
            for key, val in zip(keys, vals):
                cleaned_data[key] = val
    return cleaned_data

def apply_maps_to_modelform_fields(fields, maps, default_options=None, default_template=None):
    """
    Rearranges fields to match those defined in ``maps``.  ``maps`` is a list
    of [field_list, options_dict] pairs.  For each pair, a new map field is
    created that contans all the fields in ``field_list``.
    """
    if not maps:
        maps = [((name,),) for name,field in fields.iteritems() if isinstance(field, (MapField, GeometryField))]

    default_options = default_options or {}
    initial_data_keymap = {}

    for map_definition in maps:
        field_list = map_definition[0]
        if len(map_definition) > 1:
            options = map_definition[1]
        else:
            options = {}
        if len(map_definition) > 2:
            template = map_definition[2]
        else:
            template = default_template
        
        map_name = "_".join(field_list)
        layer_fields = []
        names = []
        min_pos = 65535 # arbitrarily high number for field ordering
        initial = []
        for field_name in field_list:
            min_pos = min(min_pos, fields.keyOrder.index(field_name))
            field = fields.pop(field_name)
            initial.append(field_name)
            if not isinstance(field.widget, (Map, BaseVectorLayer)):
                field.widget = EditableLayer(
                        options=utils.options_for_field(field))
            layer_fields.append(field)
            names.append(field_name)

        if isinstance(field, MapField):
            map_field = field
        else:
            map_opts = {}
            map_opts.update(default_options)
            map_opts.update(options or {})
            map_field = MapField(layer_fields, map_opts, layer_names=names,
                label=", ".join(forms.forms.pretty_name(f) for f in field_list),
                template=template)
        fields.insert(min_pos, map_name, map_field)
        initial_data_keymap[map_name] = initial
    return initial_data_keymap

