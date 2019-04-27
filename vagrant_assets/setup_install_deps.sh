#!/bin/bash
# Provisioning file for Vagrant
#
# Install dependencies
#

set -e

# Source configuration
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. ${THIS_DIR}/setup_config.sh

apt-get update && apt-get -y upgrade

apt-get install -y \
    bc \
    build-essential \
    git \
    nginx \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    libxml2-dev \
    libxslt-dev \
    python3-venv \
    python3-wheel \
    python3-dev \
    postgresql
