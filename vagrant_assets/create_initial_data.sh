#!/bin/bash
# Export initial data from the Django application, this script
# was used to prepare fixtures data for the Vagrant demo

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=${THIS_SCRIPT_DIR}/..
APPS="auth simplemenu"

cp -r ${ROOT_DIR}/qgis-app/static_media/packages/ ${THIS_SCRIPT_DIR}

for app in ${APPS}; do
    python manage.py dumpdata --indent 4 --format json ${app} > ${THIS_SCRIPT_DIR}/fixtures/${app}.json
done

