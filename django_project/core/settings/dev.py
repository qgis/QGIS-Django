# -*- coding: utf-8 -*-
from .project import *  # noqa

# Set Debug True for Development
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        # Newer django versions may require you to use the postgis backed
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'qgis_django',
        'USER': 'akbar',
    }
}

# Tim Email settings
EMAIL_HOST = 'localhost'
#EMAIL_PORT =
DEFAULT_FROM_EMAIL = 'noreply@qgis.org'

# TIM: Place where search indexes are stored for snippets - should be non web accessible
HAYSTACK_WHOOSH_PATH = '/home/web/qgis-django/search-index'
