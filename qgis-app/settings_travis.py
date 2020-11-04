import os

os.environ['RABBITMQ_HOST'] = 'rabbitmq'
os.environ['DATABASE_NAME'] = 'travis_ci_test'
os.environ['DATABASE_USERNAME'] = 'postgres'
os.environ['DATABASE_PASSWORD'] = ''
os.environ['DATABASE_HOST'] = 'localhost'

from settings_docker import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'travis_ci_test',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PORT': 5432,
        'TEST': {
            'NAME': 'unittests',
        }
    }
}

