# Introduction

![image](https://user-images.githubusercontent.com/178003/91536115-2356ec80-e90c-11ea-971b-f23ac72d3aea.png)

This directory contains the source code for the plugin repository server used by
the QGIS project.

This software is open source and licensed under GNU General Public License v2.0.
For licensing information, please read the COPYING file included in this directory.

## Installation

For setup, installation and backup notes, please read [INSTALL](INSTALL.md) included in this directory.

For setting up a local development environment using Vagrant please read the Vagrant [README](vagrant_assets/README.md).

To contribute to this project, please contact Tim Sutton - tim@kartoza.com


QGIS Django Project
Tim Sutton 2010

## Admin

To update QGIS versions, go to **[Admin](https://plugins.qgis.org/admin/)** -> **[Site preferences](https://plugins.qgis.org/admin/preferences/sitepreference/)**.

## Tech stack

![image](https://user-images.githubusercontent.com/178003/91535744-8c8a3000-e90b-11ea-8ca3-b6ce1bb910bd.png)

This application is based on Django, written in python and deployed on the server using
docker and rancher.

## Token based authentication

Users have the ability to generate a Simple JWT token by providing their credentials, which can then be utilized to access endpoints requiring authentication.
Users can create specific tokens for a plugin at `https://plugins.qgis.org/<package_name>/tokens/`.


```sh
# A specific plugin token can be used to upload or update a plugin version. For example:
curl \
  -H "Authorization: Bearer the_access_token" \
  https://plugins.qgis.org/plugins/<package_name>/version/add/

curl \
  -H "Authorization: Bearer the_access_token" \
  https://plugins.qgis.org/plugins/<package_name>/version/<version>/update
```

## Contributing

Please contact tim@kartoza.com if you want to contribute, or simply make a Pull Request or Issue report.

## QGIS.org

This project is part of the QGIS community effort to make the greatest GIS application in the world.
Join our efforts at [QGIS.org](https://qgis.org).
