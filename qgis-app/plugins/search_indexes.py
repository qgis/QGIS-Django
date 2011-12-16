import datetime
from haystack.indexes import *
from haystack import site
from plugins.models import Plugin


class PluginIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    created_by = CharField(model_attr='created_by')
    created_on = DateTimeField(model_attr='created_on')

    def index_queryset(self):
        """Only search in approved plugins."""
        return Plugin.objects.approved()


site.register(Plugin, PluginIndex)