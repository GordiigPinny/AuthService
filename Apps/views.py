from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from Users.permissions import WriteOnlyBySuperuser
from Apps.models import App
from Apps.serializers import AppSerializer


class AppsView(ListCreateAPIView):
    """
    Вьюха для списка и создания приложения
    """
    permission_classes = (WriteOnlyBySuperuser, )
