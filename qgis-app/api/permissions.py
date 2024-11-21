from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
import datetime
from api.models import UserOutstandingToken

MANAGER_GROUP = "Style Managers"


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsHasAccessOrReadOnly(permissions.BasePermission):
    """Custom permission, only admin, member of manager group and owner
    can edit the resource.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        is_manager = user.groups.filter(name=MANAGER_GROUP).exists()

        return user == obj.creator or user.is_staff or is_manager

class HasValidToken(BasePermission):
  def has_permission(self, request, view):
    auth_token = request.META.get("HTTP_AUTHORIZATION")
    if not str(auth_token).startswith('Bearer'):
      return False

    # Validate JWT token
    authentication = JWTAuthentication()
    try:
      validated_token = authentication.get_validated_token(auth_token[7:])
      user_id = validated_token.payload.get('user_id')
      jti = validated_token.payload.get('refresh_jti')
      token_id = OutstandingToken.objects.get(jti=jti).pk
      is_blacklisted = BlacklistedToken.objects.filter(token_id=token_id).exists()
      if not user_id or is_blacklisted:
        return False

      user = User.objects.get(pk=user_id)
      if not user:
        return False
      user_token = UserOutstandingToken.objects.get(token__pk=token_id, user=user)
      user_token.last_used_on = datetime.datetime.now()
      user_token.save()
      request.user_token = user_token
      return True
    except (InvalidToken, TokenError):
      return False