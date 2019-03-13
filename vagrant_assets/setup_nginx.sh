#!/bin/bash
# Provisioning file for Vagrant
#
# Configure nginx and systemd
#

set -e

. /vagrant/vagrant_assets/setup_config.sh

. ${INSTALL_DIR}/venv/bin/activate
pip3 install gunicorn || true

# Systemd
cp ${VAGRANT_ASSETS_DIR}/systemd/django.service /etc/systemd/system/
for var in INSTALL_DIR; do
    sed -i -e "s@##${var}##@${!var}@g" /etc/systemd/system/django.service
done


systemctl enable /etc/systemd/system/django.service
systemctl start django

# Nginx
cp ${VAGRANT_ASSETS_DIR}/nginx/django.conf /etc/nginx/sites-enabled/default
for var in INSTALL_DIR MEDIA_ROOT; do
    sed -i -e "s@##${var}##@${!var}@g" /etc/nginx/sites-enabled/default
done


service nginx restart


