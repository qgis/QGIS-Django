#!/bin/bash
# Configuration file for Vagrant provisioning scripts

export INSTALL_DIR=/var/qgis_plugins
export MEDIA_ROOT=${INSTALL_DIR}/vagrant_static/
# Set to something different than "0" to install QGIS-Django from GIT instead of
# using the local repo (mounted from Vagrant)
export FETCH_FROM_GIT="0"
export DB_NAME="qgis_django"
export DB_USER="qgis_django"
export DB_PASSWORD="qgis_django"

export LC_ALL=C
export DEBIAN_FRONTEND=noninteractive

# Make sure dirs exist
if [ ! -e ${INSTALL_DIR} ]; then
    mkdir ${INSTALL_DIR}
fi

if [ ! -e ${MEDIA_ROOT} ]; then
    mkdir -p ${MEDIA_ROOT}
fi

chown www-data.www-data ${MEDIA_ROOT}
