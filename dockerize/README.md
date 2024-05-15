# Docker compose commands Documentation

## Overview
This doc is designed for managing a Docker-based project with the ID `qgis-plugins`. It includes various commands for building, running, and maintaining both production and development environments. Below is a detailed description of each command available in the Makefile.

## Commands

### Production Commands

- **default**: Alias for the build command.
```sh
make
```

- **run**: Builds the project and runs the web, migrate, and collectstatic commands.
```sh
make run
```

- **build**: Builds Docker images for both production and development environments.
```sh
make build
```

- **db**: Starts the database container in production mode.
```sh
make db
```

- **metabase**: Starts the Metabase container after ensuring the database is running.
```sh
make metabase
```

- **web**: Starts the web container and scales the `uwsgi` service to 2 instances.
```sh
make web
```

- **dbbackups**: Starts the database backups container.
```sh
make dbbackups
```

- **certbot**: Starts the Certbot container for managing SSL certificates.
```sh
make certbot
```

- **migrate**: Runs database migrations, with the `auth` app being migrated first.
```sh
make migrate
```

- **update**-migrations: Creates new migration files based on changes in models.
```sh
make update-migrations
```

- **collectstatic**: Collects static files for the Django application.
```sh
make collectstatic
```

- **start**: Starts a specific container or all containers. Specify the container with the `c` variable.
```sh
make start c=container_name
```

- **restart**: Restarts a specific container or all containers. Specify the container with the `c` variable.
```sh
make restart c=container_name
```

- **kill**: Stops a specific container or all containers. Specify the container with the `c` variable.
```sh
make kill c=container_name
```

- **rm**: Removes all containers after stopping them.
```sh
make rm
```

- **rm-only:** Removes all containers without stopping them first.
```sh
make rm-only
```

- **dbrestore:** Restores the database from a backup file.
```sh
make dbrestore
```

- **wait-db:** Waits for the database to be ready.
```sh
make wait-db
```

- **create-test-db:** Creates a test database with PostGIS extension.
```sh
make create-test-db
```

- **rebuild_index:** Rebuilds the search index for the Django application.
```sh
make rebuild_index
```

- **uwsgi-shell:** Opens a shell in the `uwsgi` container.
```sh
make uwsgi-shell
```

- **uwsgi-reload:** Reloads the Django project in the `uwsgi` container.
```sh
make uwsgi-reload
```

- **uwsgi-errors:** Tails the error logs in the `uwsgi` container.
```sh
make uwsgi-errors
```

- **uwsgi-logs:** Tails the requests logs in the `uwsgi` container.
```sh
make uwsgi-logs
```

- **web-shell:** Opens a shell in the NGINX/web container.
```sh
make web-shell
```

- **web-logs:** Tails the logs in the NGINX/web container.
```sh
make web-logs
```

- **logs:** Tails logs for a specific container or all containers. Specify the container with the `c` variable.
```sh
make logs c=container_name
```

- **shell:** Opens a shell in a specific container. Specify the container with the `c` variable.
```sh
make shell c=container_name
```

- **exec:** Executes a specific Docker command. Specify the command with the `c` variable.
```sh
make exec c="command"
```

#### Development Commands

- **build-dev:** Builds Docker images for the development environment.
```sh
make build-dev
```

- **devweb-test:** Starts the `devweb` container for testing, ensuring the database is running.
```sh
make devweb-test
```

- **devweb:** Starts the `devweb` container for development, along with RabbitMQ, worker, and beat containers.
```sh
make devweb
```

- **devweb-runserver:** Runs the Django development server inside the `devweb` container.
```sh
make devweb-runserver
```

- **dbseed:** Seeds the database with initial data from JSON files in the `fixtures` directory.
```sh
make dbseed
```

