# Vagrant assets and setup


The main provisioning script is `provision_setup.sh`

The provisioning process is split over several files, you should be able
to re-run them individually after initial setup.

The individual steps are:

    ${VAGRANT_ASSETS_DIR}/setup_config.sh
    ${VAGRANT_ASSETS_DIR}/setup_install_deps.sh
    ${VAGRANT_ASSETS_DIR}/setup_db.sh
    ${VAGRANT_ASSETS_DIR}/setup_django.sh
    ${VAGRANT_ASSETS_DIR}/setup_nginx.sh
    ${VAGRANT_ASSETS_DIR}/setup_load_initial_data.sh


Credentials for the default user: admin/admin

## Django settings

`settings_local_vagrant.py` is used as a settings template.

## Debug mode

Django will run with `DEBUG=True` unless you change it in `settings_local_vagrant.py`

## Endpoint

The plugin app will be availble from your Host machine as:

http://localhost:8080/

## Configuration

You can change configuration by editing `setup_config.sh`

## Default code location

Depending on the value of the config variable `FETCH_FROM_GIT`, the
code base is fetched from git or mounted (by Vagrant) from local repo.


## Logging systemd unit

```
journalctl -f -u django
```