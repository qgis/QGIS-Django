# -*- coding: utf-8 -*-
from xml.dom.minidom import parse, getDOMImplementation

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

class StyleListBuilder():
    """Makes the list of styles with the metadata as a XML"""

    def __init__(self, styles):
        self.doc = getDOMImplementation().createDocument(None, "style_list", None)
        self.style_list = self.doc.documentElement
        for style in styles:
            style_ele = self.doc.createElement("style")

            stid = self.doc.createElement("id")
            stid.appendChild(self.doc.createTextNode(unicode(style.pk)))
            style_ele.appendChild(stid)

            name = self.doc.createElement("name")
            name.appendChild(self.doc.createTextNode(style.name))
            style_ele.appendChild(name)

            desc = self.doc.createElement("description")
            desc.appendChild(self.doc.createTextNode(style.description))
            style_ele.appendChild(desc)

            tags = self.doc.createElement("tags")
            tags.appendChild(self.doc.createTextNode(",".join([unicode(tag) for tag in style.tags.all()])))
            style_ele.appendChild(tags)

            cr_on = self.doc.createElement("created_on")
            cr_on.appendChild(self.doc.createTextNode(unicode(style.created_on.date())))
            style_ele.appendChild(cr_on)

            cr_by = self.doc.createElement("author")
            cr_by.setAttribute("id", str(style.created_by.pk))
            cr_by.appendChild(self.doc.createTextNode(unicode(style.created_by)))
            style_ele.appendChild(cr_by)

            qgis_v = self.doc.createElement("qgis_version")
            qgis_v.appendChild(self.doc.createTextNode(style.qgis_version))
            style_ele.appendChild(qgis_v)

            min_scale = self.doc.createElement("min_scale")
            min_scale.appendChild(self.doc.createTextNode(unicode(style.min_scale)))
            style_ele.appendChild(min_scale)

            max_scale = self.doc.createElement("max_scale")
            max_scale.appendChild(self.doc.createTextNode(unicode(style.max_scale)))
            style_ele.appendChild(max_scale)

            ren_type = self.doc.createElement("renderer")
            ren_type.appendChild(self.doc.createTextNode(style.renderer_type))
            style_ele.appendChild(ren_type)

            self.style_list.appendChild(style_ele)

    def xml(self):
        return self.style_list.toxml()
