#!/bin/bash
# Provisioning file for Vagrant
#
# Install dependencies
#

set -e

. /vagrant/vagrant_assets/setup_config.sh

apt-get update && apt-get -y upgrade

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
