#!/bin/bash
# Provisioning file for Vagrant
#
# Configure nginx and systemd
#

set -e

# Source configuration
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. ${THIS_DIR}/setup_config.sh

. ${INSTALL_DIR}/venv/bin/activate
pip3 install gunicorn || true

# Systemd service
# Number of gunicorn workers = 2*CPU_CORES+1
GUNICORN_WORKERS=$(echo "$(nproc --all) * 2 + 1" | bc)
cp ${THIS_DIR}/systemd/django.service /etc/systemd/system/
for var in INSTALL_DIR GUNICORN_WORKERS; do
    sed -i -e "s@##${var}##@${!var}@g" /etc/systemd/system/django.service
done

systemctl enable /etc/systemd/system/django.service
systemctl start django.service

# Nginx
cp ${THIS_DIR}/nginx/django.conf /etc/nginx/sites-enabled/default
for var in INSTALL_DIR MEDIA_ROOT; do
    sed -i -e "s@##${var}##@${!var}@g" /etc/nginx/sites-enabled/default
done

service nginx restart
