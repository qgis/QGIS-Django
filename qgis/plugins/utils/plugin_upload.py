#!/usr/bin/env python
# This script uploads a plugin package on the server
#
# Author: A. Pasotti

import xmlrpclib, sys, os

# Configuration
PROTOCOL='http'
SERVER='localhost'
PORT='8000'
ENDPOINT='/plugins/RPC2/'
VERBOSE=True

# Do not edit below this line

if len(sys.argv) != 4:
    print "Usage: %s compressed_package username password" % os.path.basename(sys.argv[0])
    print ''
    print 'Uploads a QGIS plugin compressed package on the server'
    sys.exit()

USERNAME=sys.argv[2]
PASSWORD=sys.argv[3] 
ADDRESS="%s://%s:%s@%s:%s%s" % (PROTOCOL, USERNAME, PASSWORD, SERVER, PORT, ENDPOINT)


server = xmlrpclib.ServerProxy('http://admin:admin@localhost:8000/plugins/RPC2/', verbose=VERBOSE)

try:
    plugin_id, version_id = server.plugin.upload(xmlrpclib.Binary(open(sys.argv[1]).read()))
    print "Plugin ID: %s" % plugin_id
    print "Version ID: %s" % version_id
except xmlrpclib.Fault, err:
    print "A fault occurred"
    print "Fault code: %d" % err.faultCode
    print "Fault string: %s" % err.faultString


