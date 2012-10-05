
Metadata
--------

Plugins mandatory metadata [#f1]_ are read from both the old `__init__.py` functions format
and (if present) the new `metadata.txt` file.

Valid metadata for the `__init__` file are:
    * `name`
    * `description`
    * `version`
    * `qgisMinimumVersion`
    * `email`
    * `author`
    * `experimental`

To avoid direct execution of python code (which would be a security issue), metadata are read from the `__init__.py` file with a simple regular expression parser which extracts the string values returned by the functions inside the `__init__.py` file, this means that if the functions do not return strings (enclosed in single or double quotes) or a boolean value (for the `experimental` entry), the metadata entry for that function will not be extracted and if the metadata is mandatory the plugin will be considered invalid.

The new `metadata.txt` file can contain other optional metadata which are read when the package is uploaded and are automatically imported.

Mandatory metadata
==================

    * `name`    
    * `qgisMinimumVersion`
    * `description`
    * `version`
    * `author`
    * `email`

Optional metadata
=================

    * `changelog`
    * `experimental`
    * `tags`
    * `homepage`
    * `repository`
    * `tracker`
    * `icon`


Example configuration file::

        ; the next section is mandatory
        [general]
        ; start of mandatory metadata
        name=HelloWorld
        qgisMinimumVersion=1.8
        description=This is a plugin for greeting the ...
            ... (going multiline) world
        version=version 1.2
        author=Alessandro Primo
        email=email@email.com
        ; end of mandatory metadata

        ; start of optional metadata

        ; experimental flag
        experimental=True

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



.. rubric:: Footnotes

.. [#f1] 'name', 'description', 'version', 'qgisMinimumVersion', 'author', 'email'
.. [#f2] Supported by metadata.txt only: 'homepage', 'changelog', 'tracker', 'repository', 'tags'
