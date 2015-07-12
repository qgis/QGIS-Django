# -*- coding: utf-8 -*-
"""Django core related settings."""
# Django settings for qgis project.
# ABP: More portable config
import os
from .utils import ABS_PATH

# Import secret key
from .secret import SECRET_KEY  # noqa

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
MEDIA_ROOT = ABS_PATH('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ABS_PATH('static')
STATIC_URL = '/static/'
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ABS_PATH('core', 'base_static'),
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'core.wsgi.application'

TEMPLATE_DIRS = (
    # project level templates
    ABS_PATH('core', 'base_templates'),
)
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
    # 'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Needed by rpc4django
    'plugins.middleware.HttpAuthMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Added by Tim for advanced loggin options
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'middleware.XForwardedForMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # project level templates
    ABS_PATH('templates'),
)


# Django native apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 'django.contrib.markup',
    'django.contrib.syndication',
    'django.contrib.flatpages',
    'django.contrib.gis',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors' : (
                "django.contrib.auth.context_processors.auth",
                'django.contrib.messages.context_processors.messages',
                # old django "django.core.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.request",
                # ABP: adds DEBUG and BASE_TEMPLATE vars
                "qgis_context_processor.additions",
            ),
        },
    },
]

LOGIN_REDIRECT_URL = '/'

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

INTERNAL_IPS = ('127.0.0.1',)
