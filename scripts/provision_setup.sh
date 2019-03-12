#!/bin/bash
# Provisioning file for Vagrant
# Install the software

set -e

INSTALL_DIR=/var/qgis_plugins
DB_NAME="qgis_django"
DB_USER="qgis_django"
DB_PASSWORD="qgis_django"

export LC_ALL=C
export DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get -y upgrade

if [ ! -e ${INSTALL_DIR} ]; then
    mkdir ${INSTALL_DIR}
fi

apt-get install -y \
    nginx \
    libldap2-dev \
    libsasl2-dev \
    libxml2-dev \
    libxslt-dev \
    python3-venv \
    python3-wheel \
    python3-dev \
    postgresql


# Note: no postgis is necessary for the plugin app

# Install the Django app
cd ${INSTALL_DIR}
git clone --single-branch --branch modernize https://github.com/qgis/QGIS-Django.git .
python3 -m venv ${INSTALL_DIR}/venv
. ${INSTALL_DIR}/venv/bin/activate
pip3 install setuptools --upgrade
pip3 install -r qgis-app/REQUIREMENTS_plugins.txt

# DB setup
sudo su - postgres -c "createdb ${DB_NAME}"
sudo su - postgres -c "psql -c \"CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';\""
sudo su - postgres -c "psql -c \"GRANT USAGE ON SCHEMA public TO ${DB_USER};\""
sudo su - postgres -c "psql -c \"GRANT CONNECT ON DATABASE ${DB_NAME} TO ${DB_USER};\""
sudo su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};\"";
sudo su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};\"";

# Setup an admin/admin user

#echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell


chown -R www-data.www-data ${INSTALL_DIR}

# Clean
echo "Cleaning up ..."
apt-get autoremove -y
apt-get clean
