from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView, Response, Request
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.contrib.auth.models import User
from Users.serializers import RegisterSerializer, UserSerializer, UserListSerializer
from Users.permissions import IsModeratorJWT


class RegisterView(APIView):
    """
    Вьюха для регистрации
    """
    def get_jwt(self, data):
        sjwt = JSONWebTokenSerializer(data=data)
        if sjwt.is_valid():
            return sjwt.object['token']
        return sjwt.errors

    def post(self, request: Request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            s.save()
            jwt = self.get_jwt(request.data)
            if isinstance(jwt, str):
                return Response({'token': jwt}, status=status.HTTP_201_CREATED)
            return Response(jwt, status=status.HTTP_400_BAD_REQUEST)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    """
    Вьюха для спискового представления юзеров
    """
    pagination_class = LimitOffsetPagination
    serializer_class = UserListSerializer
    permission_classes = (IsModeratorJWT, )

    def get_queryset(self):
        return User.objects.filter(userext__deleted_flg=False)


class UserDetailView(APIView):
    """
    Вьюха для детального представления юзера
    """
    def get(self, request: Request, pk: int):
        try:
            user = User.objects.get(pk=pk, userext__deleted_flg=False)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk: int):
        try:
            user = User.objects.get(pk=pk, userext__deleted_flg=False)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user != user and not request.user.userext.is_moderator():
            return Response({'error': 'Only user can delete itself, or moderator'}, status=status.HTTP_403_FORBIDDEN)
        if user.is_superuser:
            return Response({'error': 'No one can delete superuser, even himself'}, status=status.HTTP_403_FORBIDDEN)
        user.userext.deleted_flg = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
