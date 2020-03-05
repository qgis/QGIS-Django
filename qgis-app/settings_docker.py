from settings import *
import ast
import os
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = ast.literal_eval(os.environ.get('DEBUG', 'True'))
THUMBNAIL_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/home/web/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
# MEDIA_URL = '/media/'
# setting full MEDIA_URL to be able to use it for the feeds
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/home/web/static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',

    # ABP:
    'plugins',
    'django.contrib.humanize',
    'django.contrib.syndication',
    'bootstrap_pagination',
    'sortable_listview',
    'lib',  # Container for small tags and functions
    'sorl.thumbnail',
    'djangoratings',

    'taggit',
    'taggit_autosuggest',
    'taggit_templatetags',
    'haystack',
    'simplemenu',
    'tinymce',
    'rpc4django',

    'feedjack'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USERNAME'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': 5432,
        'TEST': {
            'NAME': 'unittests',
        }
    }
}

PAGINATION_DEFAULT_PAGINATION=5
LOGIN_REDIRECT_URL='/'
SERVE_STATIC_MEDIA = DEBUG
