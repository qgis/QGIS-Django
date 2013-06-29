# -*- coding: utf-8 -*-

from xml.dom.minidom import parse, parseString

class SymbolExtractor():
    """A class which parses the given file and returns the symbols"""
    def __init__(self, xmlfile):
        self.dom  = parse(xmlfile)
        self.symbolnodes = self.dom.getElementsByTagName( "symbol" )

    def symbols(self):
        return [{ "name" : sym.getAttribute( "name" ), "xml" : sym.toxml() } for sym in self.symbolnodes]
