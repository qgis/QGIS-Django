from functools import wraps
from django.http import HttpResponseForbidden
from rest_framework_simplejwt.authentication import JWTAuthentication
from plugins.models import Plugin
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

def has_valid_token(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    auth_token = request.META.get("HTTP_AUTHORIZATION")
    package_name = kwargs.get('package_name')
    if not str(auth_token).startswith('Bearer'):
        raise InvalidToken("Invalid token")

    # Validate JWT token
    authentication = JWTAuthentication()
    try:
      validated_token = authentication.get_validated_token(auth_token[7:])
      user = authentication.get_user(validated_token)
      plugin_id = validated_token.payload.get('plugin_id')
      jti = validated_token.payload.get('refresh_jti')
      token_id = OutstandingToken.objects.get(jti=jti).pk
      is_blacklisted = BlacklistedToken.objects.filter(token_id=token_id).exists()
      if not plugin_id or not user or is_blacklisted:
          raise InvalidToken("Invalid token")

      plugin = Plugin.objects.get(pk=plugin_id)
      if not plugin or plugin.package_name != package_name:
          raise InvalidToken("Invalid token")

      request.user = user
      return function(request, *args, **kwargs)
    except (InvalidToken, TokenError) as e:
        return HttpResponseForbidden(str(e))

  return wrap
