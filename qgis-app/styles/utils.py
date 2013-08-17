# -*- coding: utf-8 -*-
from xml.dom.minidom import parse

MIN_SCALE_DEFAULT = -4.65661e-10
MAX_SCALE_DEFAULT = 1e+08
MIN_LBLSCALE_DEFAULT = 0
MAX_LBLSCALE_DEAFULT = 1e+08

class StyleDataExtractor():
    """ A class which will parse the uploaded qml (XML) file and
    provide the necessary metadata about the style"""

    def __init__(self, xmlfile):
        # TODO Error Handling while parsing
        self.dom  = parse(xmlfile)
        self.qgisnode = self.dom.getElementsByTagName( "qgis" )[0]
        self.renderernode = self.dom.getElementsByTagName( "renderer-v2" )[0]

    def styledata(self):
        metadata = { "version" : self.qgisnode.getAttribute( "version" ),
                "minScale" : self.qgisnode.getAttribute( "minimumScale" ),
                "maxScale" : self.qgisnode.getAttribute( "maximumScale" ),
                "minLblScale" : self.qgisnode.getAttribute( "minLabelScale"),
                "maxLblScale" : self.qgisnode.getAttribute( "maxLabelScale" ),
                "scaleFlag" : self.qgisnode.getAttribute( "hasScaleBasedVisibilityFlag" ) == "1",
                "lblScaleFlag" : self.qgisnode.getAttribute( "scaleBasedLabelVisibilityFlag" ) == "1",
                "renderer" : self.renderernode.getAttribute( "type" ),
                }
        if self.qgisnode.getAttribute("minimumScale") == "":
            metadata["minScale"] = MIN_SCALE_DEFAULT
        if self.qgisnode.getAttribute("maximumScale") == "":
            metadata["maxScale"] = MAX_SCALE_DEFAULT
        if self.qgisnode.getAttribute("minLabelScale") == "":
            metadata["minLblScale"] = MIN_LBLSCALE_DEFAULT
        if self.qgisnode.getAttribute("maxLabelScale") == "":
            metadata["maxLblScale"] = MAX_LBLSCALE_DEFAULT

        return metadata

    def styleAsString(self):
        return self.dom.toxml()

