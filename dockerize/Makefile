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

build-dev:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in development mode only"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) build devweb

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
	@docker compose -p $(PROJECT_ID) up -d uwsgi web worker beat

dbbackups: db
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running dbbackups in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d dbbackups

certbot: web
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running cerbot in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up -d certbot

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
	@docker compose -p $(PROJECT_ID) up --no-deps -d rabbitmq worker beat

devweb-runserver: devweb
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in DEVELOPMENT mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) up devweb webpack

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
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	# no -it flag so we can run over remote shell
	# @docker exec $(PROJECT_ID)-web python manage.py collectstatic --noinput

reload:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Reload django project in production mode"
	@echo "------------------------------------------------------------------"
	# no -it flag so we can run over remote shell
	@docker exec $(PROJECT_ID)-web uwsgi --reload  /tmp/django.pid


kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) kill

rm: rm-only

rm-only: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing production instance!!! "
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) rm

maillogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing smtp logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose exec smtp tail -f /var/log/mail.log

mailerrorlogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing smtp error logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose exec smtp tail -f /var/log/mail.err

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

dbseed:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Seed db with JSON data from /fixtures/*.json"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec devweb bash -c 'python manage.py loaddata fixtures/*.json'

rebuild_index:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Rebuild search index in PRODUCTION mode"
	@echo "------------------------------------------------------------------"
	@docker compose -p $(PROJECT_ID) exec uwsgi bash -c 'python manage.py rebuild_index'
