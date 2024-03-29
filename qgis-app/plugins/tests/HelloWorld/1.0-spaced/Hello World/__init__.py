# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Hello World"


def description():
    return "HelloWorld"


def version():
    return "Version 1.0"


def qgisMinimumVersion():
    return "1.0"


def classFactory(iface):
    from HelloWorld import HelloWorld

    return HelloWorld(iface)


def icon():
    """
    Icon
    """
    return "icon.png"
