from rest_framework.permissions import BasePermission
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
