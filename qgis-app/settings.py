# coding=utf-8
# Django settings for qgis project.
# ABP: More portable config
import os

from datetime import timedelta
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

TEMPLATE_DEBUG = False
DEBUG = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "America/Chicago"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = SITE_ROOT + "/static/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/static/"
MEDIA_URL_FOLDER = "/static/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = "/admin/"

STATIC_URL = "/static_media/"
STATIC_ROOT = SITE_ROOT + "/static_media/"


STATICFILES_DIRS = [
    os.path.join(SITE_ROOT, "static"),
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# Make this unique, and don't share it with anybody.
SECRET_KEY = "y2vu=4qarl)p=g_blq_c4afk!p6u_cor1gy1k@05ro=+tf7+)g"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
    "django.template.loaders.eggs.Loader",  # Tim: needed on live server for CAB
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Needed by rpc4django
    "plugins.middleware.HttpAuthMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    # Added by Tim for advanced loggin options
    "django.middleware.cache.FetchFromCacheMiddleware",
    "middleware.XForwardedForMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, "templates"),
)


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    # Uncomment the next line to enable the admin:
    "django.contrib.admin",
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    "django.contrib.staticfiles",
    # ABP:
    "plugins",
    #'pagination',
    "django.contrib.humanize",
    #'django.contrib.markup',
    "django.contrib.syndication",
    #'ratings',
    "taggit",
    "taggit_autosuggest",
    "taggit_templatetags",
    "haystack",
    "django.contrib.flatpages",
    "simplemenu",
    "tinymce",
    # Tim for django snippets app support
    #'cab', #the django snippets app itself
    "debug_toolbar",
    # Tim for command extensions so we can run feedjack cron using python manage.py runscript
    "django_extensions",
    # Sam for Users map
    #'django.contrib.gis',
    #'users',
    "olwidget",
    # Tim for blog planet / feed aggregator
    "feedjack",
    # For users app thumbs
    "sorl.thumbnail",
    # RPC
    "rpc4django",
    #'south',
    "djangoratings",
    "lib",
    "endless_pagination",
    "userexport",
    "bootstrap_pagination",
    "sortable_listview",
    "user_map",
    "leaflet",
    "bootstrapform",
    "rest_framework",
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    "rest_framework_gis",
    "preferences",
    # styles:
    "styles",
    "matomo"
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                # ABP: adds DEBUG and BASE_TEMPLATE vars
                "qgis_context_processor.additions",
                "preferences.context_processors.preferences_cp",
            ),
        },
    },
]

ACCOUNT_ACTIVATION_DAYS = (
    7  # One-week activation window; you may, of course, use a different value
)

LOGIN_REDIRECT_URL = "/"

# Added by Tim for snippets (and possibly other site search support)
# HAYSTACK_SITECONF = 'search_sites'
# django.core.exceptions.ImproperlyConfigured: The HAYSTACK_SITECONF setting is no longer used & can be removed.
HAYSTACK_CONNECTIONS = {"default": "whoosh"}
HAYSTACK_WHOOSH_PATH = SITE_ROOT + "/search-index"

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(os.path.dirname(__file__), "whoosh_index"),
    },
}

# Migration: see http://django-haystack.readthedocs.org/en/latest/migration_from_1_to_2.html#removal-of-realtimesearchindex
HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"

# Added by Tim for database based caching
# See http://docs.djangoproject.com/en/dev/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        # "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": "cache_table",
    }
}

CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_PREFIX = ""
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True


TAGGIT_TAGCLOUD_MIN = 10
TAGGIT_TAGCLOUD_MAX = 30

INTERNAL_IPS = ("127.0.0.1",)

DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_HOST_USER", "automation")


# TINYMCE_JS_URL = 'http://debug.example.org/tiny_mce/tiny_mce_src.js'
TINYMCE_DEFAULT_CONFIG = {
    "plugins": "table,spellchecker,paste,searchreplace",
    "theme": "advanced",
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True

# Default number of items per page
PAGINATION_DEFAULT_PAGINATION = 20
PAGINATION_DEFAULT_PAGINATION_HUB = 30

# rpc4django
RPC4DJANGO_LOG_REQUESTS_RESPONSES = False

# QGIS dev list email address for plugins approval notifications
QGIS_DEV_MAILING_LIST_ADDRESS = ""

# Media URL for taggit autocomplete
TAGGIT_AUTOCOMPLETE_JS_BASE_URL = MEDIA_ROOT + "/taggit-autocomplete"

# Taggit: exclude tags with less than specified tagged items
TAGCLOUD_COUNT_GTE = 3

# ratings
RATINGS_VOTES_PER_IP = 10000

# OLWIDGET_STATIC_URL='/static/olwidget/'

DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

# THUMBNAIL_ENGINE = "sorl.thumbnail.engines.convert_engine.Engine"

USER_MAP = {
    "project_name": "QGIS",
    "favicon_file": "/static/images/qgis-icon-32x32.png",
    "login_view": "login",
    "marker": {
        "iconUrl": "/static/images/qgis-icon-32x32.png",
        "iconSize": [32, 32],
        "popupAnchor": [0, -15],
    },
    "leaflet_config": {
        "TILES": [
            (
                # The title
                "OpenStreetMap",
                # Tile's URL
                "http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
                # More valid leaflet option is passed here
                {
                    "attribution": '© <a href="http://www.openstreetmap.org" '
                    'target="_parent">OpenStreetMap'
                    "</a> and contributors, under an <a "
                    'href="http://www.openstreetmap.org/copyright" '
                    'target="_parent">open '
                    "license</a>",
                    "maxZoom": 18,
                    "minZoom": 2,
                    "noWrap": True,
                },
            )
        ]
    },
    "roles": [
        {"id": 1, "name": "User", "badge": "user_map/img/badge-user.png"},
        {"id": 2, "name": "Trainer", "badge": "user_map/img/badge-trainer.png"},
        {"id": 3, "name": "Developer", "badge": "user_map/img/badge-developer.png"},
    ],
    "api_user_fields": ["username"],
}


# When run behind a proxy
USE_X_FORWARDED_HOST = True


# auth overrids
from settings_auth import *

# Local settings overrides
# Must be the last!
try:
    from settings_local import *
except ImportError:
    pass


# Local settings might have enabled DEBUG, load additional modules here

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]

BROKER_URL = "amqp://guest:guest@%s:5672//" % os.environ["RABBITMQ_HOST"]
RESULT_BACKEND = BROKER_URL
CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Token access and refresh validity
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
}

MATOMO_SITE_ID="1"
MATOMO_URL="//matomo.qgis.org/"
