#!/bin/bash
# Provisioning file for Vagrant
#
# Load fixtures and test initial data
#

set -e

# Source configuration
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. ${THIS_DIR}/setup_config.sh

. ${INSTALL_DIR}/venv/bin/activate

cd ${INSTALL_DIR}/qgis-app

# Load initial data
APPS="auth simplemenu"
for app in ${APPS}; do
    python manage.py loaddata --settings=settings_local_vagrant --app ${app} ${THIS_DIR}/fixtures/${app}.json
done

# Install test plugin
cd ${INSTALL_DIR}/qgis-app/plugins/tests/
python3 upload_test.py
