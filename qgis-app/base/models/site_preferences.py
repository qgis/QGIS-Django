from django.db import models
from preferences.models import Preferences


class SitePreference(Preferences):
    __module__ = 'preferences.models'
    qgis_versions = models.TextField(
        default='',
        blank=True,
        help_text='QGIS versions that will be used to '
                  'generate the plugins_xml, separated by comma.'
    )
