# -*- coding: utf-8 -*-
from symbols.models import Symbol
from xml.dom.minidom import getDOMImplementation, parse, parseString

class SymbolExtractor():
    """A class which parses the given file and returns the symbols"""
    def __init__(self, xmlfile):
        self.dom  = parse(xmlfile)
        self.symbolnodes = self.dom.getElementsByTagName( "symbol" )
        self.colorrampnodes = self.dom.getElementsByTagName( "colorramp" )

    def symbols(self):
        symbols = [{ "name" : sym.getAttribute( "name" ),
            "type" : sym.getAttribute( "type" ),
            "xml" : sym.toxml(),
            "is_symbol" : True } for sym in self.symbolnodes]
        ramps = [{ "name" : cr.getAttribute( "name" ),
            "type" : cr.getAttribute( "type" ),
            "xml" : cr.toxml(),
            "is_symbol" : False } for cr in self.colorrampnodes]
        return symbols + ramps

class XMLBuilder():
    """A Class which gets the objects of Symbol Model and returns a xml of qgis_style"""
    def __init__(self, symbols):
        self.doc = getDOMImplementation().createDocument(None, "qgis_style", None)
        self.style = self.doc.documentElement
        self.style.setAttribute("version", "1")
        symbols_ele = self.doc.createElement("symbols")
        self.style.appendChild(symbols_ele)
        ramps_ele = self.doc.createElement("colorramps")
        self.style.appendChild(ramps_ele)
        for symbol in symbols:
            symdom = parseString(symbol.xml).documentElement
            if symbol.is_symbol:
                symbols_ele.appendChild(symdom)
            else:
                ramps_ele.appendChild(symdom)

    def xml(self):
        return self.style.toxml()
