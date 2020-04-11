from typing import Union
from django.contrib.auth.models import User


def get_token_from_header(request) -> Union[str, None]:
    """
    Получаем токен из header'а запроса
    """
    try:
        return request.META.get['HTTP_AUTHORIZATION'][7:]
    except KeyError:
        return None


def is_moderator(user: User) -> bool:
    """
    Проверка юзера на модератора
    """
    return user.groups.filter(name='moderators').exists()
