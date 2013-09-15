# Django settings for qgis project.
# ABP: More portable config
import os
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

TEMPLATE_DEBUG = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'y2vu=4qarl)p=g_blq_c4afk!p6u_cor1gy1k@05ro=+tf7+)g'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader', #Tim: needed on live server for CAB
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Needed by rpc4django
    'plugins.middleware.HttpAuthMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    # ABP:
    'django_sorting.middleware.SortingMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Added by Tim for advanced loggin options
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates'),
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    )


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # ABP:
    'plugins',
    'django_sorting',
    'pagination',
    'django.contrib.humanize',
    'django.contrib.comments',
    'django.contrib.markup',
    'django.contrib.syndication',
    #'ratings',
    'taggit',
    'taggit_autosuggest',
    'taggit_templatetags',
    'haystack',
    'django.contrib.flatpages',
    'simplemenu',
    'tinymce',
    # Tim for django snippets app support
    #'cab', #the django snippets app itself
    # Tim for Debug toolbar
    'debug_toolbar',
    # Tim for command extensions so we can run feedjack cron using python manage.py runscript
    'django_extensions',
    # Sam for Users map
    'django.contrib.gis',
    'users',
    'olwidget',
    # Tim for blog planet / feed aggregator
    'feedjack',
    # For users app thumbs
    'sorl.thumbnail',
    # RPC
    'rpc4django',
    'south',
    'djangoratings',
    'lib',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    'django.contrib.messages.context_processors.messages',
    # old django "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    # ABP: adds DEBUG and BASE_TEMPLATE vars
    "qgis_context_processor.additions",
)

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value

LOGIN_REDIRECT_URL='/'

# Added by Tim for snippets (and possibly other site search support)
HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = SITE_ROOT + '/search-index'


# Added by Tim for database based caching
# See http://docs.djangoproject.com/en/dev/topics/cache/
CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    'LOCATION': 'cache_table',
  }
}

CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_PREFIX = ''
CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True


TAGGIT_TAGCLOUD_MIN=10
TAGGIT_TAGCLOUD_MAX=30

INTERNAL_IPS = ('127.0.0.1',)

DEFAULT_FROM_EMAIL='noreply@qgis.org'


#TINYMCE_JS_URL = 'http://debug.example.org/tiny_mce/tiny_mce_src.js'
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

#QGIS dev list email address for plugins approval notifications
QGIS_DEV_MAILING_LIST_ADDRESS=''

# Media URL for taggit autocomplete
TAGGIT_AUTOCOMPLETE_JS_BASE_URL=MEDIA_ROOT + '/taggit-autocomplete'

# Taggit: exclude tags with less than specified tagged items
TAGCLOUD_COUNT_GTE=3

# ratings
RATINGS_VOTES_PER_IP=10000

OLWIDGET_STATIC_URL='/static/olwidget/'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

# auth overrids
from settings_auth import *

# Local settings overrides
# Must be the last!
try:
    from settings_local import *
except ImportError:
    pass
