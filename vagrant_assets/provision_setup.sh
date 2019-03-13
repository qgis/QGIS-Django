#!/bin/bash
# Provisioning file for Vagrant
#
# Install all required system software packages
#


set -e

. /vagrant/vagrant_assets/config.sh


${VAGRANT_ASSETS_DIR}/install_deps.sh
${VAGRANT_ASSETS_DIR}/db_setup.sh
${VAGRANT_ASSETS_DIR}/django_setup.sh
${VAGRANT_ASSETS_DIR}/load_initial_data.sh


# Fix permissions
chown -R www-data.www-data ${INSTALL_DIR}

# Clean up
echo "Cleaning up ..."
apt-get autoremove -y
apt-get clean
