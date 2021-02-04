from rest_framework import permissions

MANAGER_GROUP = 'Style Managers'


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
