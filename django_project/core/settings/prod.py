# -*- coding: utf-8 -*-
from .project import *  # noqa

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

MIDDLEWARE_CLASSES += (
    'django.middleware.gzip.GZipMiddleware',
)

# Comment if you are not running behind proxy
USE_X_FORWARDED_HOST = True

# Set debug to false for production
DEBUG = TEMPLATE_DEBUG = False
