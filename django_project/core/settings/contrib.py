# -*- coding: utf-8 -*-
"""Third-party related settings."""
from .base import *  # noqa

# Third party apps
INSTALLED_APPS += (
    'taggit',
    'taggit_autosuggest',
    'taggit_templatetags',
    'haystack',
    'simplemenu',
    'tinymce',
    'pagination',
    # For users app thumbs
    'sorl.thumbnail',
    # RPC
    'rpc4django',
    # 'ratings',
    'djangoratings',
    # Tim for command extensions so we can run feedjack cron using python
    # manage.py runscript
    'django_extensions',
    # Tim for blog planet / feed aggregator
    'feedjack',
    'lib',
    'endless_pagination',
    'bootstrap_pagination',
    'sortable_listview',
    # Tim for django snippets app support
    # 'cab', #the django snippets app itself
    # Tim for Debug toolbar
    'debug_toolbar',
    # Sam for Users map
    'olwidget',
)

# Django Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# Added by Tim for snippets (and possibly other site search support)
# HAYSTACK_SITECONF = 'search_sites'
# django.core.exceptions.ImproperlyConfigured:
# The HAYSTACK_SITECONF setting is no longer used & can be removed.
HAYSTACK_CONNECTIONS = {
    'default': 'whoosh'
}
HAYSTACK_WHOOSH_PATH = ABS_PATH('search-index')
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': ABS_PATH('whoosh_index'),
    },
}
# Migration: see http://django-haystack.readthedocs.org/en/latest/migration_from_1_to_2.html#removal-of-realtimesearchindex
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# TAGGIT
TAGGIT_TAGCLOUD_MIN=10
TAGGIT_TAGCLOUD_MAX=30
# Taggit: exclude tags with less than specified tagged items
TAGCLOUD_COUNT_GTE=3


# Media URL for taggit autocomplete
TAGGIT_AUTOCOMPLETE_JS_BASE_URL=MEDIA_ROOT + '/taggit-autocomplete'

# TINYMCE_JS_URL = 'http://debug.example.org/tiny_mce/tiny_mce_src.js'
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True

# Default number of items per page
PAGINATION_DEFAULT_PAGINATION = 20

# rpc4django
RPC4DJANGO_LOG_REQUESTS_RESPONSES = False

# ratings
RATINGS_VOTES_PER_IP=10000

#OLWIDGET_STATIC_URL='/static/olwidget/'

# Sorl Thumbnail
THUMBNAIL_ENGINE='sorl.thumbnail.engines.convert_engine.Engine'

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value

#Tim for google maps in user community page
#qgis-django.localhost
GOOGLE_API_KEY='ABQIAAAAyZw9WlHOs4CazzwUByOgZxQok5WFiNcwymBq4ClbhSeQY6fSMhTl0KHT2Donh18dLk3P4AC4ddOarA'
