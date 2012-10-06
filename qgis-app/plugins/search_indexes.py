import datetime
from haystack.indexes import *
from haystack import site
from plugins.models import Plugin


class PluginIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    created_by = CharField(model_attr='created_by')
    created_on = DateTimeField(model_attr='created_on')
    # We add this for autocomplete.
    name_auto = NgramField(model_attr='name')
    description_auto = NgramField(model_attr='description')
    
    def index_queryset(self):
        """Only search in approved plugins."""
        return Plugin.approved_objects.all()


site.register(Plugin, PluginIndex)
