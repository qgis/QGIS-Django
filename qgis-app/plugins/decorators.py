from functools import wraps
from django.http import HttpResponseForbidden
from rest_framework_simplejwt.authentication import JWTAuthentication
from plugins.models import Plugin
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

def has_valid_token(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    auth_token = request.META.get("HTTP_AUTHORIZATION")
    package_name = kwargs.get('package_name')
    # Return this decorator if user is authenticated or token is not specified
    if request.user.is_authenticated or not str(auth_token).startswith('Bearer'):
        return function(request, *args, **kwargs)

    # Validate JWT token
    authentication = JWTAuthentication()
    try:
      validated_token = authentication.get_validated_token(auth_token[7:])
      user = authentication.get_user(validated_token)
      plugin_id = validated_token.payload.get('plugin_id')
      if not plugin_id or not user:
          raise InvalidToken("Invalid token")
      request.user = user

      plugin = Plugin.objects.get(pk=plugin_id)
      if not plugin or plugin.package_name != package_name:
          raise InvalidToken("Invalid token")

      return function(request, *args, **kwargs)
    except (InvalidToken, TokenError) as e:
        return HttpResponseForbidden(str(e))

  return wrap
