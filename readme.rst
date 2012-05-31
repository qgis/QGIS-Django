Introduction
================================================================================

This directory contains the source code for django apps used in the QGIS 
project.

For licensing information, please read COPYING file included in this directory.

For setup and installation notes, please read INSTALL included in this 
directory.

To contribute to this project, please contact Tim Sutton - tim@linfiniti.com

Tim Sutton 

November 2010

QGIS Django Project
This document describes the procedure for setting up the QGIS Django Project.
Tim Sutton 2010

Installation
================================================================================

For the terminally lazy
--------------------------------------------------------------------------------

For a readonly checkout do::

  sudo apt-get install libldap2-dev libsasl2-dev python-gdal libxml2-dev \
      libxslt-dev
  git clone git@github.com:qgis/qgis-django.git
  cd qgis-django
  sudo easy_install virtualenv
  virtualenv --no-site-packages python
  source python/bin/activate
  pip install -r REQUIREMENTS.txt

Install some manual dependencies needed for django-snippets (make sure your
virtual env is active)::

  git clone https://github.com/coleifer/django-amazon-resources.git
  cd django-amazon-resources/
  python setup.py install
  cd ..

Now install qgis snippets (a fork of django snippets)::

  git clone git@github.com:qgis/qgis-snippets.git
  cd qgis-snippets
  python setup.py install
  cd ..

.. note::  Important note: the server currently use python 2.5, due to some
   strange incompatibilities between compressed egg format and Django
   init machinery, in order to recognise "haystack" search stuff, the
   cab EGG must be uncompressed such as the final directories (in the 
   virtualenv) are::

     python/lib/python2.5/site-packages/cab-0.2.0-py2.5.egg/cab
     python/lib/python2.5/site-packages/cab-0.2.0-py2.5.egg/EGG-INFO

Install PostGIS::

  sudo apt-get install postgresql-8.4-postgis

Copy the settings template::

  cd qgis
  cp settings_local.py.templ settings_local.py

Then run the createdb script::

  ./createdb.sh

.. note:: If you already have postgis installed in your template1 db, 
   just do the following command rather than running the createdb script::

      createdb qgis-trunk


.. note:: Remember to source the activate script to enabled the python
   virtual environment::

     source python/bin/activate

Modify settings_local.py to include the correct username and pwd for the
db connection and then sync the database::

  cd qgis-app
  python manage.py syncdb

Then run the project using the embedded test server::

  python manage.py runserver

Then point your browser at::

  http://localhost:8000

Deploying a live site using wsgi
--------------------------------------------------------------------------------

We need to configure Apache for having wsgi support::

  cd /etc/apache/sites-available
  sudo cp <path to qgis-django>/apache/apache.virtenv.conf.example 
    qgis-django.conf

Now modify qgis-django.conf to your needs (making sure paths and web url are 
correct) then::

  sudo a2ensite qgis-django.conf
  sudo /etc/init.d/apache2 reload

Updating the search indexes
--------------------------------------------------------------------------------

The haystack search indexes should be created after initial install::

  python manage.py create_index

There after they should be updated regularly e.g. using a 5 min cron job::

  python manage.py update_index

Cache setup
--------------------------------------------------------------------------------

We will use database based caching here (see `django (caching) 
<http://docs.djangoproject.com/en/dev/topics/cache/>`.

Make sure your virtual env is set up and then create a cache table::

  python manage.py createcachetable cache_table

.. note:: The cache backend is required for the planet / feedjack to work 
   properly

Feedjack Update
--------------------------------------------------------------------------------

The Blog Planet requires feedjack_update.py to run at regular intervals to keep
the site fresh. The update_planet.sh shell script sets up the environment and
runs feedjack_update.py.

The script requires you to set SITE_DIR to point at the Django site directory 
prior to first use.

The script must be run by a user that has permissions to the site directory.

To install as a cron, use the following (adjust the paths for your site)::

  */2 * * * * /home/web/qgis-django/update_planet.sh \
    1>>/tmp/planet_update.log 2>>/tmp/planet_update.err

Pootle
================================================================================

Installation
------------

Pootle is included in the qgis-django project as a git submodule and is a
Django project.
To replicate the structure, we can include it in the same manner in the git 
project::

   git submodule add git@github.com:capooti/pootle.git pootle
   git submodule
   git submodule init pootle
   git submodule update pootle
   git status
   git commit -m "Import pootle as a git submodule" -a
   git push

To obtain updates to the pootle submodule, the procedure is:

   cd <your sphinx project>/pootle
   git pull
   cd ..

Create a virtual env, activate it and install requirements::

    virtualenv --no-site-packages --python=python2.5 pootle_env
    . pootle_env/bin/activate
    sudo apt-get install libxml2-dev libxslt-dev
    pip install -r REQUIREMENTS.txt

Then commit the fact that the submodule now tracks a different SHA1::

   git commit -am "Updates pootle to latest version"
   
Modify pootle/settings.py to include the correct username and pwd for the
db connection and then stat the Pootle server with the ./PootleServer
command (note that the first time that the Pootle server will be started the
database will be synced)::

  cd pootle
  ./manage runserver

Then point your browser at::

  http://localhost:8000
  
Deploying a live site using wsgi
--------------------------------------------------------------------------------

We need to configure Apache for having wsgi support::

  cd /etc/apache/sites-available
  sudo cp <path to qgis-django>/apache/pootle.virtenv.conf.example 
    pootle.conf

Now modify pootle.conf to your needs (making sure paths and web url are 
correct) then::

  sudo a2ensite pootle.conf
  sudo /etc/init.d/apache2 reload

Planned applications
================================================================================

* plugins - a django app for managing the QGIS python plugin repository
* users - a django app for creating a community map and some demographics
* snippets - a django app for users to share python and c++ snippets showing howi
  to program QGIS
* styles - a django app for users to publish the QGIS styles they have created
* symbols - a django app for users to publish symbols (svg/png etc) they have created
* planet - a blog aggregator for people blogging with QGIS related stuff
* gallery - a gallery of maps made with QGIS
* web links - a list of sites, articles etc. that feature QGIS prominantly
* pootle - a django project for managing localization of QGI documentation

