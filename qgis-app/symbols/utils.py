# -*- coding: utf-8 -*-
from symbols.models import Symbol
from xml.dom.minidom import getDOMImplementation, parse, parseString

class SymbolExtractor():
    """A class which parses the given file and returns the symbols"""
    def __init__(self, xmlfile):
        self.dom  = parse(xmlfile)
        self.symbolnodes = self.dom.getElementsByTagName( "symbol" )

    def symbols(self):
        return [{ "name" : sym.getAttribute( "name" ),
            "type" : sym.getAttribute( "type" ),
            "xml" : sym.toxml() } for sym in self.symbolnodes]

class XMLBuilder():
    """A Class which gets the objects of Symbol Model and returns a xml of qgis_style"""
    def __init__(self, symbols):
        self.doc = getDOMImplementation().createDocument(None, "qgis_style", None)
        self.style = self.doc.documentElement
        self.style.setAttribute("version", "1")
        symbols_ele = self.doc.createElement("symbols")
        self.style.appendChild(symbols_ele)
        for symbol in symbols:
            symdom = parseString(symbol.xml).documentElement
            symbols_ele.appendChild(symdom)

    def xml(self):
        return self.style.toxml()
