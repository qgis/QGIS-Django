
Metadata
--------

.. important::
    All metadata must be in UTF-8 encoding.

Plugins mandatory metadata are read from both the old `__init__.py` functions format
and (if present) the new `metadata.txt` file.

.. warning::
    If `qgisMinimumVersion` is set to a value lower than 1.8 the old `__init__.py` is required in addition the new `metadata.txt` file.

Valid metadata for the `__init__` file are:
    * `name`
    * `description`
    * `version`
    * `qgisMinimumVersion`
    * `email`
    * `author`
    * `experimental`
    * `category`



To avoid direct execution of python code (which would be a security issue),
metadata are read from the `__init__.py` file with a simple regular expression
parser which extracts the string values returned by the functions inside the
`__init__.py` file, this means that if the functions do not return strings
(enclosed in single or double quotes) or a boolean value (for the
`experimental` entry), the metadata entry for that function will not be
extracted and if the metadata is mandatory the plugin will be considered
invalid.

The new `metadata.txt` file can contain other optional metadata which are read
when the package is uploaded and are automatically imported.

Mandatory metadata
==================

* `name`: a short string  containing the name of the plugin
* `qgisMinimumVersion`: dotted notation of minimum QGIS version
* `description`: longer text which describes the plugin
* `version`: short string with the version dotted notation
* `author`: author name
* `email`: email of the author, will *not* be shown on the web site


Optional metadata
=================

* `changelog`: string, can be multiline, no HTML allowed
* `experimental`: boolean flag, `True` or `False`
* `tags`: comma separated list, spaces are allowe inside individual tags
* `homepage`: a valid URL
* `repository`: a valid URL for the source code repository
* `tracker`: a valid URL for tickets and bug reports
* `icon`: a file name or a relative path (relative to the base folder of the compressed package)


.. notice::
    If `qgisMaximumVersion` is not set, it is automatically set to the major version plus `.99`. For example, if `qgisMinimumVersion` is `1.7` and `qgisMaximumVersion` is not set, `qgisMaximumVersion` becomes `1.99`.


Example configuration file::

        ; the next section is mandatory
        [general]
        ; start of mandatory metadata
        name=HelloWorld
        qgisMinimumVersion=1.8
        qgisMaximumVersion=1.9
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

