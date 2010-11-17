import os
import sys

ROOT_PROJECT_FOLDER = os.path.dirname(__file__)
path1 = os.path.join(ROOT_PROJECT_FOLDER, '..')
path2 = os.path.join(ROOT_PROJECT_FOLDER, '..', 'qgis')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
sys.path.append( path1 )
sys.path.append( path2 )
file("/tmp/log.txt","wt").write( str(sys.path) )

