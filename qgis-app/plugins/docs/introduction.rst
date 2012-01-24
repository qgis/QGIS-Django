========================
QGIS Plugins application
========================

Author: Alessandro Pasotti (www.itopen.it)

The Plugin model
================

The plugin model represents a QGIS plugin and holds general informations such as title and description and icon.

The plugin can have zero or more *owners*, *owners* have the same permissions of the original plugin creator.

Permissions
-----------

These rules have been implemented:

* every registered user can add a new plugin
* *staff* users can approve or disapprove all plugin versions
* users which have the special permission `plugins.can_approve` get the versions they upload automatically approved
* users which have the special permission `plugins.can_approve` can approve versions uploaded by others as long as they are in the list of the plugin *owners*
* a particular plugin can be deleted and edited only by *staff* users and plugin *owners*
* if a user without `plugins.can_approve` permission uploads a new version, the plugin version is automatically unapproved.


Trust management
----------------

Staff members can grant *trust* to selected plugin creators setting `plugins.can_approve` permission through the front-end application.

The plugin details view offers direct links to grant trust to the plugin creator or the plugin *owners*.


The PluginVersion model
=======================

Each plugin can have several versions, a version specify the minimum QGIS version needed in order to run that particular plugin version and other informations such as if the version belongs to the "stable" o to the "experimental" branch.

Validation
----------

The validation takes place in the PluginVersions forms, at loading time, the compressed file is checked for:

* file size <= `PLUGIN_MAX_UPLOAD_SIZE`
* zip contains `__init__.py` in first level dir
* `__init__.py` must contain valid metadata:
    * `name`
    * `description`
    * `version`
    * `qgisMinimumVersion`


* `version` must be unique whithin a plugin
* there must be one and only *last* versions in each plugin's branch

At the time of plugin creation, the name of the folder inside the compressed file is stored in the variable `package_name`, this value must be unique and cannot be changed. `package_name` is also used to build SEF URLs, for example the plugin's page for the plugin *Hello World Plugin* with `package_name` *HelloWorld* is `<http://plugins.qgis.org/plugins/HelloWorld/>`_

The `package_name` (and hence the first level folder inside the compressed zip file) cannot contain only ASCI letters (A-Z and a-z), digits and the characters underscore (_) and minus (-) and cannot start with a
digit.

Example from the `HelloWorld` plugin compressed zip file::

    Archive:  plugins/tests/HelloWorld/HelloWorld_1.2.zip
    Length     Date       Time    Name
    ---------  ---------- -----   ----
        0      2011-11-13 15:05   HelloWorld/
        1304   2011-11-13 12:40   HelloWorld/icon.png
        374    2011-11-13 15:05   HelloWorld/metadata.txt
        1094   2011-11-13 12:40   HelloWorld/HelloWorld.py
        396    2011-11-13 12:40   HelloWorld/__init__.py
    ---------                     -------
        3168                      5 files



Metadata
--------

Plugins mandatory metadata [#f1]_ are read from both the old `__init__.py` functions format
and (if present) the new `metadata.txt` file.

To avoid direct execution of python code (which would be a security issue), metadata are read from the `__init__.py` file with a simple regular expression parser which extracts the string values returned by the functions inside the `__init__.py` file, this means that if the functions do not return strings (enclosed in single or double quotes), the metadata entry for that function will not be extracted and if the metadata is mandatory the plugin will be considered invalid.

The new `metadata.txt` file can contain other optional metadata which are read when the package is uploaded and are automatically imported.

Example configuration file::

        ; the next section is mandatory
        [general]
        name=HelloWorld
        qgisMinimumVersion=1.8
        description=This is a plugin for greeting the
            (going multiline) world
        version=version 1.2
        ; end of mandatory metadata

        ; start of optional metadata
        changelog=this is a very
            very
            very
            very
            very
            very long multiline changelog

        ; tags are in comma separated value format, spaces are allowed
        tags=wkt,raster,hello world

        ; these metadata can be empty
        ; in a future version of the web application it will
        ; be probably possible to create a project on redmine
        ; if they are not filled
        homepage=http://www.itopen.it
        tracker=http://bugs.itopen.it
        repository=http://www.itopen.it/repo
        icon=icon.png

        ; experimental flag
        experimental=True

        ; deprecated flag (applies to the whole plugin and not only to the uploaded version)
        deprecated=False

Configuration
=============

All values can be overridden in `settings.py`

========================== ============= =======================
Parameter                  Default       Notes
========================== ============= =======================
PLUGINS_STORAGE_PATH       packages
PLUGIN_MAX_UPLOAD_SIZE     1048576       in bytes
PLUGINS_FRESH_DAYS         30            days
MAIL_FROM_ADDRESS          -             used in email notifications
PLUGIN_REQUIRED_METADATA   [#f1]_        used in validator
PLUGIN_OPTIONAL_METADATA   [#f2]_        used in validator
========================== ============= =======================


.. rubric:: Footnotes

.. [#f1] 'name', 'description', 'version', 'qgisMinimumVersion'
.. [#f2] Supported by metadata.txt only: 'homepage', 'changelog', 'tracker', 'repository', 'tags'
