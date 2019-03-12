from django.apps import AppConfig

class PluginsConfig(AppConfig):
    name = 'plugins'
    verbose_name = "QGIS Plugins"

    def ready(self):
        from . import api
