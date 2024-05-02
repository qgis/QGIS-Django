#!/usr/bin/env bash


# Run daily on crontab e.g.
#  Your cron job will be run at: (5 times displayed)
#
#    2021-11-08 11:10:00 UTC
#    2021-11-09 11:10:00 UTC
#    2021-11-10 11:10:00 UTC
#    2021-11-11 11:10:00 UTC
#    2021-11-12 11:10:00 UTC
#    ...etc

#25 11 * * * /bin/bash /home/web/QGIS-Django/dockerize/scripts/renew_ssl.sh > /tmp/ssl-renewal-logs.txt


docker compose -f /home/web/QGIS-Django/dockerize/docker-compose.yml -p qgis-plugins run certbot renew