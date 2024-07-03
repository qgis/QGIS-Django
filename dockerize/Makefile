PROJECT_ID := qgis-plugins

SHELL := /bin/bash

# ----------------------------------------------------------------------------
#    P R O D U C T I O N     C O M M A N D S
# ----------------------------------------------------------------------------
default: build
run: build web migrate collectstatic

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production and development mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) build


db:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running db in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d db

metabase: db
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running metabase in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d metabase

web: db
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d --scale uwsgi=2 web worker beat dbbackups

certbot: web
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running cerbot in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d certbot

migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate static in production mode"
	@echo "------------------------------------------------------------------"
	@#http://stackoverflow.com/questions/29689365/auth-user-error-with-django-1-8-and-syncdb-migrate
	@#and
	@#http://stackoverflow.com/questions/3143635/how-to-ignore-mv-error
	@# We add the '-' prefix to the next line as the migration may fail
	@# but we want to continue anyway.
	@#We need to migrate accounts first as it has a reference to user model
	-@docker compose -p $(PROJECT_ID) exec uwsgi python manage.py migrate auth
	@docker compose -p $(PROJECT_ID) exec uwsgi python manage.py migrate

update-migrations:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running update migrations in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi python manage.py makemigrations

collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) run uwsgi python manage.py collectstatic --noinput

start:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Starting a specific container(s) in production mode. Use web if you want to start all."
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d $(c)

restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restarting all or a specific container(s) in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) restart $(c)

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing all or a specific container(s) in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) kill $(c)

rm: rm-only

rm-only: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing production instance!!! "
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) rm

dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from backups/latest.dmp in production mode"
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	@echo "stopping uwsgi container"
	@docker compose -p $(PROJECT_ID) stop uwsgi
	@echo "Dropping the gis and metabase databases"
	-@docker compose -p $(PROJECT_ID) exec db su - postgres -c "dropdb --force gis"
	-@docker compose -p $(PROJECT_ID) exec db su - postgres -c "dropdb --force metabase"
	@echo "Creating the gis and metabase databases"
	-@docker compose -p $(PROJECT_ID) exec db su - postgres -c "createdb -O docker -T template1 gis"
	-@docker compose -p $(PROJECT_ID) exec db su - postgres -c "createdb -O docker -T template1 metabase"
	@echo "Restore database from backups/latest-gis.dmp"
	-@docker compose -p $(PROJECT_ID) exec db su - postgres -c "pg_restore -c /backups/latest-gis.dmp -d gis"
	-@docker compose -p $(PROJECT_ID) exec db su - postgres -c "pg_restore -c /backups/latest-metabase.dmp -d metabase"
	@echo "starting uwsgi container"
	@docker compose -p $(PROJECT_ID) up -d uwsgi

wait-db:
	@docker compose -p $(PROJECT_ID) exec db su - postgres -c "until pg_isready; do sleep 5; done"

create-test-db:
	@docker compose -p $(PROJECT_ID) exec db su - postgres -c "psql -c 'create database test_db;'"
	@docker compose -p $(PROJECT_ID) exec db su - postgres -c "psql -d test_db -c 'create extension postgis;'"

rebuild_index:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Rebuild search index in PRODUCTION mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi bash -c 'python manage.py rebuild_index'

uwsgi-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling into the uwsgi container(s)"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi bash 

uwsgi-reload:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Reload django project in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi bash -c 'uwsgi uwsgi --reload  /tmp/django.pid'

uwsgi-errors:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Tailing errors in the uwsgi container(s)"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi bash -c 'tail -f /var/log/uwsgi-errors.log'

uwsgi-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Tailing access logs in uwsgi container(s)"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi bash -c 'tail -f /var/log/uwsgi-requests.log'

web-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling into the NGINX/WEB container(s)"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec web bash 

web-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Tailing logs in NGINX/WEB container(s)"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) logs -f web

logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Tailing all logs or a specific container"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) logs -f $(c)

shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling into a specific container"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec $(c) bash

exec:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Execute a specific docker command"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) $(c)

# ----------------------------------------------------------------------------
#    D E V E L O P M E N T    C O M M A N D S
# ----------------------------------------------------------------------------

build-dev:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in development mode only"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) build devweb

devweb-test: db
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in TESTING mode"
	@echo "------------------------------------------------------------------"
	@docker compose up --no-deps -d devweb

devweb: db
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in DEVELOPMENT mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up --no-deps -d devweb rabbitmq worker beat

devweb-runserver: devweb
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in DEVELOPMENT mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec devweb python manage.py runserver 0.0.0.0:8081

dbseed:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Seed db with JSON data from /fixtures/*.json"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec devweb bash -c 'python manage.py loaddata fixtures/*.json'