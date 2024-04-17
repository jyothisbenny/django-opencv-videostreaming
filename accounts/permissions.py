from rest_framework.permissions import BasePermission


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class UserPermissions(BasePermission):
    metadata_perms = AllowAny()
    enough_perms = None
    global_perms = None
    retrieve_perms = IsSuperUser()
    create_perms = AllowAny()
    update_perms = IsAuthenticated()
    partial_update_perms = IsSuperUser()
    destroy_perms = IsSuperUser()
    list_perms = IsSuperUser()
    login_perms = AllowAny()
    logout_perms = IsAuthenticated()
