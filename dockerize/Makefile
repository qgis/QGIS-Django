dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from backups/latest.dmp in production mode"
	@echo "------------------------------------------------------------------"
	@# - prefix causes command to continue even if it fails
	-@docker-compose exec db su - postgres -c "dropdb gis"
	@docker-compose exec db su - postgres -c "createdb -O docker -T template_postgis gis"
	@docker-compose exec db bash -c 'pg_restore /backups/latest.dmp | su - postgres -c "psql gis"'
