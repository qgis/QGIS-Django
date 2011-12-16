import xmlrpclib
server = xmlrpclib.ServerProxy('http://admin:admin@localhost:8000/plugins/RPC2/')
handle = open("HelloWorld.zip", "rb")
blob = xmlrpclib.Binary(handle.read())
server.plugin.upload(blob)

