from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from Users.utils import is_moderator


class WriteOnlyByMeAndSuperuser(BasePermission):
    """
    Пермишн на запись только юзером, который делает запрос, или суперюзером
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user_id = int(view.kwargs['pk'])
        return (IsAuthenticated().has_permission(request, view) and (request.user.pk == user_id)) or \
            IsSuperuserJWT().has_permission(request, view)


class IsModeratorJWT(BasePermission):
    """
    Пермишн, просматривающий ДЖВТ-токен
    """

    def has_permission(self, request, view):
        user = request.user
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
        user = request.user
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
