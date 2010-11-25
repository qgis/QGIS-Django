========================
QGIS Plugins application
========================

The Plugin model
================

The plugin model represents a QGIS plugin and holds general informations such as title and description.

Users who can edit or delete the plugin are listed in the *owners* field, the plugin original uploader is listed by default.

Permissions
-----------

These rules have been implemented:

* every registered user can add a plugin
* only *staff* users and users which have the special permission `plugins.can_publish` can publish a plugin
* a particular plugin can be edited and deleted only by *staff* users and users listed in plugin's *owners* field
* plugin's versions can be uploaded, edited and deleted only by *staff* users and users listed in plugin's *owners* field
* if a user without `plugins.can_publish` permission uploads a new version, the plugin becomes unpublished



The PluginVersion model
=======================

Each plugin can have several versions, a version specify the minimum QGIS version needed in order to run that particular plugin version and other informations such as if the version belongs to the "stable" o to the "experimental" branch.

Validation
----------

The validation takes place in the PluginVersions forms, at loading time, the compressed file is checked for:

* file size <= PLUGIN_MAX_UPLOAD_SIZE
* zip contains __init__.py in first level dir
* __init__.py must contain valid metadata:
    * name
    * description
    * version
    * qgisMinimumVersion



Configuration
=============

All values can be overridden in `settings.py`

PLUGINS_STORAGE_PATH
PLUGIN_MAX_UPLOAD_SIZE

