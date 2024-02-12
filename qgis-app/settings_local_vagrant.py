import os

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
THUMBNAIL_DEBUG = DEBUG  # sorl.thumbnail verbose debug

ALLOWED_HOSTS = ["*"]

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

# Override assets for Vagrant
# User uploaded files
MEDIA_ROOT = "/home/dimas/Documents/Kartoza/QGIS-Django/vagrant_static/"

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


STATICFILES_DIRS = [
    os.path.join(SITE_ROOT, "static"),
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
            ),
        },
    },
]


ADMINS = (("Admin", "admin@email.com"),)

MANAGERS = ADMINS
# Tell django which clients may receive debug messages...used by django-debug-toolbar
INTERNAL_IPS = ("127.0.0.1", "")

# Disable for prod machine
TEMPLATE_DEBUG = DEBUG
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG

DATABASES = {
    "default": {
        # Newer django versions may require you to use the postgis backed
        #'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        "ENGINE": "django.db.backends.postgresql_psycopg2",  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': 'qgis-django-plugins.db',                      # Or path to database file if using sqlite3.
        "NAME": "qgis_django",  # Or path to database file if using sqlite3.
        "USER": "qgis_django",  # Not used with sqlite3.
        "PASSWORD": "qgis_django",  # Not used with sqlite3.
        "HOST": "127.0.0.1",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "5432",  # Set to empty string for default. Not used with sqlite3.
    }
}

# Tim for google maps in user community page
# qgis-django.localhost
GOOGLE_API_KEY = "ABQIAAAAyZw9WlHOs4CazzwUByOgZxQok5WFiNcwymBq4ClbhSeQY6fSMhTl0KHT2Donh18dLk3P4AC4ddOarA"

PAGINATION_DEFAULT_PAGINATION = 5
LOGIN_REDIRECT_URL = "/"
SERVE_STATIC_MEDIA = DEBUG

# TIM: Place where search indexes are stored for snippets - should be non web accessible
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(os.path.dirname(__file__), "whoosh_index"),
    },
}

# Tim Email settings
EMAIL_HOST = "localhost"
# EMAIL_PORT =
DEFAULT_FROM_EMAIL = "automation@qgis.org"

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
    "django.contrib.flatpages",
    # ABP:
    "plugins",
    "django.contrib.humanize",
    "django.contrib.syndication",
    "bootstrap_pagination",
    "sortable_listview",
    "lib",  # Container for small tags and functions
    "sorl.thumbnail",
    "djangoratings",
    "taggit",
    "taggit_autosuggest",
    "taggit_templatetags",
    "haystack",
    "simplemenu",
    "tinymce",
    "rpc4django",
]

PLUGIN_MAX_UPLOAD_SIZE = 1024 * 1024 * 20

if DEBUG:
    INSTALLED_APPS.append("django_extensions")
