# Vagrant assets

The main provisioning script is `provision_setup.sh`

The provisioning process is split over several files, you should be able
to re-run them individually after initial setup.

The individual steps are:

    ${VAGRANT_ASSETS_DIR}/install_deps.sh
    ${VAGRANT_ASSETS_DIR}/db_setup.sh
    ${VAGRANT_ASSETS_DIR}/django_setup.sh
    ${VAGRANT_ASSETS_DIR}/load_initial_data.sh


## Django settings

`settings_local_vagrant.py` is used as a settings template.

## Endpoint

The plugin app will be availble from your Host machine as:

http://localhost:8080/

## Configuration

You can change configuration by editing `config.sh`

## Default code location

Depending on the value of the config variable `FETCH_FROM_GIT`, the
code base is fetched from git or mounted (by Vagrant) from local repo.
