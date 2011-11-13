# Custom middleware
from django.contrib.auth.models import User


class HttpAuthMiddleware:
    """
    Simple HTTP-Basic auth for testing webservices
    """
    def process_request(self, request):
        auth_basic = request.META.get('HTTP_AUTHORIZATION')
        if auth_basic:
            import base64
            try:
                username , dummy,  password = base64.decodestring(auth_basic[6:]).partition(':')
                user = User.objects.get(username=username)
                if user.check_password(password):
                   request.user = user
            except User.DoesNotExist:
                pass
        return None
