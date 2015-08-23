PROJECT_ID := qgisdjango

SHELL := /bin/bash


# ----------------------------------------------------------------------------
#    P R O D U C T I O N     C O M M A N D S
# ----------------------------------------------------------------------------
default: web
run: permissions web migrate collectstatic update_index create_cache

deploy: build run
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Bringing up fresh instance "
	@echo "You can access it on http://localhost:61200"
	@echo "------------------------------------------------------------------"

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) build

status:
	@echo
	@echo "-------------------------------------------------------------------"
	@echo "Status of all running production containers"
	@echo "-------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) ps

web:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d web
	@# Dont confuse this with the dbbackup make command below
	@# This one runs the postgis-backup cron container
	@# We add --no-recreate so that it does not destroy & recreate the db container
	@docker-compose -p $(PROJECT_ID) up --no-recreate --no-deps -d dbbackups

permissions:
	# Probably we want something more granular here....
	# Your sudo password will be needed to set the file permissions
	# on logs, media, static and pg dirs
	@if [ ! -d "logs" ]; then mkdir logs; fi
	@if [ ! -d "media" ]; then mkdir media; fi
	@if [ ! -d "static" ]; then mkdir static; fi
	@if [ ! -d "backups" ]; then mkdir backups; fi
	@if [ -d "logs" ]; then sudo chmod -R a+rwx logs; fi
	@if [ -d "media" ]; then sudo chmod -R a+rwx media; fi
	@if [ -d "static" ]; then sudo chmod -R a+rwx static; fi
	@if [ -d "backups" ]; then sudo chmod -R a+rwx backups; fi

db:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running db in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d db

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
	-@docker-compose -p $(PROJECT_ID) run uwsgi python manage.py migrate auth
	@docker-compose -p $(PROJECT_ID) run uwsgi python manage.py migrate

collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in production mode"
	@echo "------------------------------------------------------------------"
	#@docker-compose -p $(PROJECT_ID) run uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i $(PROJECT_ID)_uwsgi_1 python manage.py collectstatic --noinput

reload:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Reload django project in production mode"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_uwsgi_1 uwsgi --reload  /tmp/django.pid

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) kill

rm: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing production instance!!! "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) rm

logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing uwsgi logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs uwsgi

dblogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing db logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs db

weblogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing web logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) logs web

shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) run uwsgi /bin/bash

superuser:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Creating a superuser in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) run uwsgi python manage.py createsuperuser

update_index:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Update haystack index"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) run uwsgi python manage.py update_index

create_cache:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create cache table for caching"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) run uwsgi python manage.py createcachetable cache_table

dbshell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in production database"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_db_1 psql -U docker -h localhost gis

dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from backups/latest.dmp in production mode"
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	-@docker exec -t -i $(PROJECT_ID)_db_1 su - postgres -c "dropdb gis"
	@docker exec -t -i $(PROJECT_ID)_db_1 su - postgres -c "createdb -O docker -T template_postgis gis"
	@docker exec -t -i $(PROJECT_ID)_db_1 pg_restore /backups/latest.dmp | docker exec -i $(PROJECT_ID)_db_1 su - postgres -c "psql gis"

dbbackup:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create `date +%d-%B-%Y`.dmp in production mode"
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	@docker exec -t -i $(PROJECT_ID)_dbbackups_1 /backups.sh
	@docker exec -t -i $(PROJECT_ID)_dbbackups_1 cat /var/log/cron.log | tail -2 | head -1 | awk '{print $4}'
	-@if [ ! -f "backups/latest.dmp" ]; then ln -s backups/`date +%Y`/`date +%B`/PG_$(PROJECT_ID)_`date +%d-%B-%Y`.dmp backups/latest.dmp; fi
	@echo "Backup should be at: backups/`date +%Y`/`date +%B`/PG_$(PROJECT_ID)_`date +%d-%B-%Y`.dmp"

sentry:
	@echo
	@echo "--------------------------"
	@echo "Running sentry production mode"
	@echo "--------------------------"
	@docker-compose  -p $(PROJECT_ID) up -d sentry

maillogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing smtp logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_smtp_1 tail -f /var/log/mail.log

mailerrorlogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing smtp error logs in production mode"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)_smtp_1 tail -f /var/log/mail.err


# ----------------------------------------------------------------------------
#    DEVELOPMENT C O M M A N D S
# --no-deps will attach to prod deps if running
# after running you will have ssh and web ports open (see dockerfile for no's)
# and you can set your pycharm to use the python in the container
# ----------------------------------------------------------------------------
dev-run: dev-web dev-loaddata

dev-web:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in DEVELOPMENT mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up --no-deps -d devweb

dev-loaddata:
	@echo
	@echo "-------------------------------------------------------------------"
	@echo "Load all the fixtures"
	@echo "-------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) run devweb python manage.py loaddata django_flatpage simplemenu_menu simplemenu_urlitem simplemenu_menuitem auth


# ----------------------------------------------------------------------------
#    S T A G I N G     C O M M A N D S
# ----------------------------------------------------------------------------
staging-run: staging-web staging-migrate staging-collectstatic staging-update_index staging-create_cache

staging-deploy: staging-build staging-run
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Bringing up fresh staging instance "
	@echo "You can access it on http://localhost:61201"
	@echo "------------------------------------------------------------------"

staging-build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in staging mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging build

staging-status:
	@echo
	@echo "-------------------------------------------------------------------"
	@echo "Status of all running staging containers"
	@echo "-------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging ps

staging-web:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in staging mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging up -d stagingweb

staging-migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate static in staging mode"
	@echo "------------------------------------------------------------------"
	@#http://stackoverflow.com/questions/29689365/auth-user-error-with-django-1-8-and-syncdb-migrate
	@#and
	@#http://stackoverflow.com/questions/3143635/how-to-ignore-mv-error
	@# We add the '-' prefix to the next line as the migration may fail
	@# but we want to continue anyway.
	@#We need to migrate accounts first as it has a reference to user model
	-@docker-compose -p $(PROJECT_ID)-staging run uwsgi python manage.py migrate auth
	@docker-compose -p $(PROJECT_ID)-staging run uwsgi python manage.py migrate

staging-collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in staging mode"
	@echo "------------------------------------------------------------------"
	#@docker-compose -p $(PROJECT_ID)-staging run uwsgi python manage.py collectstatic --noinput
	#We need to run collect static in the same context as the running
	# uwsgi container it seems so I use docker exec here
	@docker exec -t -i $(PROJECT_ID)staging_uwsgi_1 python manage.py collectstatic --noinput

staging-kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in staging mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging kill

staging-rm: staging-kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing staging instance!!! "
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging rm

staging-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing uwsgi logs in staging mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging logs uwsgi

staging-weblogs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Showing web logs in staging mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging logs stagingweb

staging-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in staging mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging run uwsgi /bin/bash

staging-dbshell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in in staging database"
	@echo "------------------------------------------------------------------"
	@docker exec -t -i $(PROJECT_ID)staging_db_1 psql -U docker -h localhost gis

staging-update_index:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Update haystack index"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging run uwsgi python manage.py update_index

staging-create_cache:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create cache table for caching"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID)-staging run uwsgi python manage.py createcachetable cache_table
