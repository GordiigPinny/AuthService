from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response, Request
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from Users.serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from Users.permissions import WriteOnlyByMeAndSuperuser


class RegisterView(APIView):
    """
    Вьюха для регистрации
    """
    def post(self, request: Request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            s.save()
            token = RefreshToken.for_user(s.instance)
            data = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    """
    Вьюха для возврата инфы о юзере по токену
    """
    permission_classes = (IsAuthenticated, )

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
    permission_classes = (WriteOnlyByMeAndSuperuser, )

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
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    """
    Вьюха смены пароля
    """
    permission_classes = (IsAuthenticated, )

    def patch(self, request: Request):
        user = request.user
        s = ChangePasswordSerializer(data=request.data, instance=user)
        if s.is_valid():
            s.save()
            token = RefreshToken.for_user(s.instance)
            data = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            return Response(data, status=status.HTTP_202_ACCEPTED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
