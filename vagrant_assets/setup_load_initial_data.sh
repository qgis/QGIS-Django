#!/bin/bash
# Provisioning file for Vagrant
#
# Load fixtures and test initial data
#

set -e

. /vagrant/vagrant_assets/setup_config.sh
. ${INSTALL_DIR}/venv/bin/activate

cd ${INSTALL_DIR}/qgis-app

# Load initial data
APPS="auth simplemenu"
for app in ${APPS}; do
    python manage.py loaddata --settings=settings_local_vagrant --app ${app} ${VAGRANT_ASSETS_DIR}/fixtures/${app}.json
done

# Install test plugin
cd ${INSTALL_DIR}/qgis-app/plugins/tests/
python3 upload_test.py
