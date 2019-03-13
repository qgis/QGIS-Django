#!/bin/bash
# Configuration file for Vagrant provisioning scripts

export INSTALL_DIR=/var/qgis_plugins
export STATIC_DIR=${INSTALL_DIR}/static
export VAGRANT_ASSETS_DIR=/vagrant/vagrant_assets/
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

if [ ! -e ${STATIC_DIR} ]; then
    mkdir -p ${STATIC_DIR}
fi