from xmlrpc import client

server = client.ServerProxy("http://admin:admin@localhost:80/plugins/RPC2/")
handle = open("HelloWorld.zip", "rb")
blob = client.Binary(handle.read())
server.plugin.upload(blob)
