SHELL := /bin/bash

# Override this vars on the command line:
# Example:
# $ make DB_OPTS="-h 10.96.0.167 -U dbuser" DB_NAME="dbname"

DB_NAME=qgis-django
DB_OPTS=
PRJ_DIR=./qgis

all:
	@echo "See Makefile source for targets details"


run: kill_server
	cd $(PRJ_DIR) && python manage.py runserver 0.0.0.0:8000 

kill_server:
	@if /usr/sbin/lsof -i :8000; then \
		echo "WARNING: A server was already listening on port 8000, I'm trying to kill it"; \
		kill -9 `/usr/sbin/lsof -i :8000 -Fp|cut -c2-`; \
	fi

clean:
	find $(PRJ_DIR) -type f -name "*.pyc" -exec rm -rf \{\} \;

cleardb: clean
	-dropdb $(DB_NAME) $(DB_OPTS)
	createdb $(DB_NAME) $(DB_OPTS) -E UTF-8 -T template_postgis


reset: cleardb
	cd $(PRJ_DIR) && python manage.py syncdb --noinput
	cd $(PRJ_DIR) && python manage.py loaddata fixtures/auth.json
	@echo 'Login as admin/admin'


runlocal: kill_server
	cd $(PRJ_DIR) && python manage.py runserver 0.0.0.0:8000

shell:
	cd $(PRJ_DIR) && python manage.py shell --plain

ishell:
	cd $(PRJ_DIR) && python manage.py shell


dumpauth:
	cd $(PRJ_DIR) && python manage.py  dumpdata --format=json --indent=4 auth.user > fixtures/auth.json

dumpplugins:
	cd $(PRJ_DIR) && python manage.py  dumpdata --format=json --indent=4 plugins.plugin plugins.pluginversion > fixtures/plugins.json

loadplugins:
	cd $(PRJ_DIR) && python manage.py loaddata fixtures/plugins.json

check:
	$(MAKE) -C qgis $@
