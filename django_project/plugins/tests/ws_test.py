"""

Test services



>>> from django.test.client import Client
>>> c = Client()
>>> from xmlrpclib import *
>>> from django.core.management import call_command


Utility function:

def xmldecode(r):p, u = getparser();p.feed(r.content);p.close();return u._stack[0]

>>> def xmldecode(r):
...     p, u = getparser()
...     p.feed(r.content)
...     p.close()
...     return u._stack[0]




>>> c.login(username='admin', password='admin')
True

>>> xmldecode(c.post('/plugins/RPC2', dumps(tuple(), "plugins.auth_test") , content_type = 'text/xml'))
1

>>> c.logout()




"""
