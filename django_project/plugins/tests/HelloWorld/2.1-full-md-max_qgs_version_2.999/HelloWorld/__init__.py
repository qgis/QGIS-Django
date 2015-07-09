# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
  from HelloWorld import HelloWorld
  return HelloWorld(iface)
