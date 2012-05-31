import os
import sys

ROOT_DIR = '/home/capooti/git/github/qgis/qgis-django'
APP_DIR = '/home/capooti/git/github/qgis/qgis-django/pootle'
LOCAL_APPS_DIR = '/home/capooti/git/github/qgis/qgis-django/pootle/local_apps'
EXT_APPS_DIR = '/home/capooti/git/github/qgis/qgis-django/pootle/external_apps'
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, LOCAL_APPS_DIR)
sys.path.insert(0, EXT_APPS_DIR)

import site
VE_DIR = '/home/capooti/git/github/qgis/qgis-django/pootle/pootle_env/lib/python2.5/site-packages'
site.addsitedir(VE_DIR)

import django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'
application = django.core.handlers.wsgi.WSGIHandler()

