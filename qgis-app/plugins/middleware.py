# Custom middleware to handle HTTP_AUTHORIZATION
# Author: A. Pasotti

from django.contrib import auth
from rest_framework_simplejwt.authentication import JWTAuthentication

def HttpAuthMiddleware(get_response):
    """
    Simple HTTP-Basic auth for testing webservices
    """

    def middleware(request):
        auth_basic = request.META.get("HTTP_AUTHORIZATION")
        if auth_basic and not str(auth_basic).startswith('Bearer'):
            import base64

            username, dummy, password = base64.decodebytes(
                auth_basic[6:].encode("utf8")
            ).partition(b":")
            username = username.decode("utf8")
            password = password.decode("utf8")

            user = auth.authenticate(username=username, password=password)
            if user:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.
                request.user = user
                auth.login(request, user)
        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
