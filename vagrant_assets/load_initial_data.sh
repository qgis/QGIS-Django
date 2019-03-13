#!/bin/bash
# Provisioning file for Vagrant
#
# Load fixtures and test initial data
#

set -e

. /vagrant/vagrant_assets/config.sh
. ${INSTALL_DIR}/venv/bin/activate

cd ${INSTALL_DIR}/qgis-app

# Load initial data
APPS="auth simplemenu plugins contenttypes djangoratings"
cp -r ${VAGRANT_ASSETS_DIR}/packages/ ${STATIC_DIR}

for app in ${APPS}; do
    python manage.py loaddata --app ${app} ${VAGRANT_ASSETS_DIR}/fixtures/${app}.json
done
