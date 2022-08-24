from haystack import indexes
from plugins.models import Plugin


class PluginIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_by = indexes.CharField(model_attr="created_by")
    created_on = indexes.DateTimeField(model_attr="created_on")
    # We add this for autocomplete.
    name_auto = indexes.EdgeNgramField(model_attr="name")
    description_auto = indexes.EdgeNgramField(model_attr="description")
    about_auto = indexes.EdgeNgramField(model_attr="about", default="")
    package_name_auto = indexes.EdgeNgramField(model_attr="package_name", default="")

    def get_model(self):
        return Plugin

    def index_queryset(self, using=None):
        """Only search in approved plugins."""
        return Plugin.approved_objects.all()
