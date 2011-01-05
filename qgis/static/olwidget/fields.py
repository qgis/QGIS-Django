from django import forms

from olwidget.widgets import Map, EditableLayer, InfoLayer

class MapField(forms.fields.Field):
    """
    Container field for map fields.  Similar to MultiValueField, but with
    greater autonomy of component fields.  Values are never "compressed" or
    "decompressed", and component fields are consulted for their validation.
    Example:

        MapField([EditableLayerField(), InfoLayerField()], options={...})

    """
    def __init__(self, fields=None, options=None, layer_names=None, 
            template=None, **kwargs):
        # create map widget enclosing vector layers and options
        if not fields:
            fields = [EditableLayerField()]
        layers = [field.widget for field in fields]
        self.fields = fields
        kwargs['widget'] = kwargs.get('widget', 
                Map(layers, options, template, layer_names))
        super(MapField, self).__init__(fields, **kwargs)

    def validate(self, value):
        pass

    def clean(self, value):
        """
        Return an array with the value from each layer.
        """
        return [f.clean(v) for v,f in zip(value, self.fields)]

class EditableLayerField(forms.fields.CharField):
    """
    Equivalent to:

    forms.CharField(widget=EditableLayer(options={...}))
    """
    def __init__(self, options=None, **kwargs):
        kwargs['widget'] = kwargs.get('widget', EditableLayer(options))
        super(EditableLayerField, self).__init__(**kwargs)

class InfoLayerField(forms.fields.CharField):
    """
    Equivalent to:

    forms.CharField(widget=InfoLayer(info=[...], options={...}), 
            required=False)
    """
    def __init__(self, info, options=None, **kwargs):
        kwargs['widget'] = kwargs.get('widget', InfoLayer(info, options))
        kwargs['required'] = False
        super(InfoLayerField, self).__init__(**kwargs)
