# Architecture

The plugin application is installed in a virtualenv, Django is served
through a wsgi application invoked by gunicorn.

Gunicorn is started by systemd and connected to nginx by a unix socket (also
controlled by systemd), the number gunicorn workers is automatically set to
CPU*2+1 as suggested by official documentation.


# Vagrant assets and setup

The main provisioning script is `provision_setup.sh`

The provisioning process is split over several files, you should be able
to (re-)run them individually after initial setup.

The individual steps are:

    setup_config.sh  # Sourced by all other scripts, holds the configuration for the installation
    setup_install_deps.sh  # Installs dependencies
    setup_db.sh  # Setup the DB
    setup_django.sh  #  Installs Django and the plugin app
    setup_nginx.sh  # Configures the web server
    setup_load_initial_data.sh  # Loads some initial data


Credentials for the default user: admin/admin

## Django settings

`settings_local_vagrant.py` is used as a settings template.

## Debug mode

Django will run with `DEBUG=True` unless you change it in `settings_local_vagrant.py`

## Endpoint

The plugin app will be available from your Host machine as:

http://localhost:8080/

## Configuration

You can change configuration by editing `setup_config.sh`

## Default code location

Depending on the value of the config variable `FETCH_FROM_GIT`, the
code base is fetched from git or mounted (by Vagrant) from local repo.


## Logging systemd unit

```
journalctl -f -u django.service
journalctl -f -u django.socket
```
