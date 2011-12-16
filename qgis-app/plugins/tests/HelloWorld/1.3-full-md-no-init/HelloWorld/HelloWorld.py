# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


class HelloWorld:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def initGui(self):
        # Create action that will start plugin
        self.action = QAction(QIcon(":/plugins/"), "&HelloWorld", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("activated()"), self.hello_world)

        # Add toolbar button and menu item
        self.iface.addPluginToMenu("HelloWorld", self.action)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("HelloWorld",self.action)



    # run
    def hello_world(self):
        QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('HelloWorld', "HelloWorld"), QCoreApplication.translate('HelloWorld', "HelloWorld"))
        return




if __name__ == "__main__":
    pass
