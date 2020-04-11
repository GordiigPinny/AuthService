from rest_framework.permissions import BasePermission, SAFE_METHODS
from Users.utils import get_user_from_token, get_token_from_header, is_moderator


class IsModeratorJWT(BasePermission):
    """
    Пермишн, просматривающий ДЖВТ-токен
    """
    def has_permission(self, request, view):
        token = get_token_from_header(request)
        user = get_user_from_token(token)
        if user is not None:
            return is_moderator(user)
        return False


class WriteOnlyByModerator(BasePermission):
    """
    Пермишн на запись только модератором
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsModeratorJWT().has_permission(request, view)


class IsSuperuserJWT(BasePermission):
    """
    Пермишн только для суперюзера
    """
    def has_permission(self, request, view):
        token = get_token_from_header(request)
        user = get_user_from_token(token)
        if user is not None:
            return user.is_superuser
        return False


class WriteOnlyBySuperuser(BasePermission):
    """
    Пермишн на запись только суперюзером
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsSuperuserJWT().has_permission(request, view)
