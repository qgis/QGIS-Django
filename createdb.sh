#!/bin/bash
createdb qgis-django
createlang plpgsql qgis-django
psql qgis-django < /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
psql qgis-django < /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql

