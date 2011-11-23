# Custom middleware to handle HTTP_AUTHORIZATION
# Author: A. Pasotti

from django.contrib.auth.models import User
from django.contrib import auth


class HttpAuthMiddleware:
    """
    Simple HTTP-Basic auth for testing webservices
    """
    def process_request(self, request):
        auth_basic = request.META.get('HTTP_AUTHORIZATION')
        if auth_basic:
            import base64
            username , dummy,  password = base64.decodestring(auth_basic[6:]).partition(':')

            user = auth.authenticate(username=username, password=password)
            if user:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.
                request.user = user
                auth.login(request, user)

