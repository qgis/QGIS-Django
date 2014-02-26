import datetime
from haystack.indexes import *
from haystack import indexes
from plugins.models import Plugin


class PluginIndex(indexes.SearchIndex, indexes.Indexable):
    text = CharField(document=True, use_template=True)
    created_by = CharField(model_attr='created_by')
    created_on = DateTimeField(model_attr='created_on')
    # We add this for autocomplete.
    name_auto = EdgeNgramField(model_attr='name')
    description_auto = EdgeNgramField(model_attr='description')

    def get_model(self):
        return Plugin

    def index_queryset(self):
        """Only search in approved plugins."""
        return self.get_model().approved_objects.all()

