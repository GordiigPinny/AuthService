from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView, Response, Request
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.contrib.auth.models import User
from Users.serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from Users.utils import is_moderator
from Users.permissions import IsModeratorJWT


class RegisterView(APIView):
    """
    Вьюха для регистрации
    """
    def get_jwt(self, data):
        sjwt = JSONWebTokenSerializer(data=data)
        if sjwt.is_valid():
            return sjwt.object['token'], sjwt.object['user']
        return sjwt.errors

    def post(self, request: Request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            s.save()
            jwt_user = self.get_jwt(request.data)
            if isinstance(jwt_user, tuple):
                jwt, user = jwt_user
                return Response({'token': jwt, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
            return Response(jwt_user, status=status.HTTP_400_BAD_REQUEST)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    """
    Вьюха для возврата инфы о юзере по токену
    """
    def get(self, request: Request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(ListAPIView):
    """
    Вьюха для спискового представления юзеров
    """
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class UserDetailView(APIView):
    """
    Вьюха для детального представления юзера
    """
    def get(self, request: Request, pk: int):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk: int):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user != user and not is_moderator(request.user):
            return Response({'error': 'Only user can delete itself, or moderator'}, status=status.HTTP_403_FORBIDDEN)
        if user.is_superuser:
            return Response({'error': 'No one can delete superuser, even himself'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    """
    Вьюха смены пароля
    """
    def get_jwt(self, data):
        sjwt = JSONWebTokenSerializer(data=data)
        if sjwt.is_valid():
            return sjwt.object['token']
        return sjwt.errors

    def patch(self, request: Request, pk: int):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user.id != request.user.id and not user.is_superuser:
            return Response({'error', 'Нельзя менять чужой пароль'}, status=status.HTTP_403_FORBIDDEN)
        s = ChangePasswordSerializer(data=request.data, instance=user)
        if s.is_valid():
            s.save()
            jwt = self.get_jwt({'username': user.username, 'password': request.data['password']})
            if isinstance(jwt, str):
                return Response({'token': jwt}, status=status.HTTP_202_ACCEPTED)
            return Response(jwt, status=status.HTTP_400_BAD_REQUEST)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
