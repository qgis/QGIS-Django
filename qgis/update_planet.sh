cd /home/web/qgis-django
# Run feedjack_update.py to update the planet postings
SITE_DIR=/home/web/qgis-django
source $SITE_DIR/python/bin/activate
# set up the environment
export PYTHONPATH=$SITE_DIR:$SITE_DIR/qgis
export DJANGO_SETTINGS_MODULE=qgis.settings
# update the feeds
feedjack_update.py

