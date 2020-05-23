from rest_framework import status
from rest_framework.views import Response, Request, APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.exceptions import TokenBackendError
from jwt.exceptions import InvalidTokenError
from Users.permissions import IsSuperuserJWT
from Apps.models import App
from Apps.serializers import AppSerializer, AppForTokenSerializer
from Apps.tokens import AppRefreshToken


class AppsView(ListCreateAPIView):
    """
    Вьюха для списка и создания приложения
    """
    permission_classes = (IsSuperuserJWT, )
    pagination_class = LimitOffsetPagination
    serializer_class = AppSerializer

    def get_queryset(self):
        return App.objects.all()

    def post(self, request: Request, *args, **kwargs):
        s = AppSerializer(data=request.data)
        if s.is_valid():
            app = s.save()
            token = AppRefreshToken.for_user(app)
            data = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class AppView(RetrieveDestroyAPIView):
    """
    Вьюха для показа и удаления приложения
    """
    permission_classes = (IsSuperuserJWT, )
    serializer_class = AppSerializer

    def get_queryset(self):
        return App.objects.all()


class GetTokenPairForApp(APIView):
    """
    Возврат токенов по app_name, app_secret
    """
    authentication_classes = ()

    def post(self, request: Request):
        s = AppForTokenSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            app = App.objects.get(id=s['id'].value, secret=s['secret'].value, is_internal=True)
        except App.DoesNotExist:
            return Response({'error': 'Wrong app credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        token = AppRefreshToken.for_user(app)
        data = {
            'access': str(token.access_token),
            'refresh': str(token),
        }
        return Response(data, status=status.HTTP_200_OK)


class VerifyTokenForApp(APIView):
    """
    200 если токен еще валиден, иначе 401
    """
    authentication_classes = ()

    def post(self, request: Request):
        try:
            token = request.data['token']
        except KeyError:
            return Response({'error': 'Field "token" is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = token_backend.decode(token)
        except (InvalidTokenError, TokenBackendError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            token_type = payload['token_type']
        except KeyError:
            return Response({'error': 'No token_type for token was given'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            app_id = payload['id']
        except KeyError:
            return Response({'error', 'No id in token'}, status=status.HTTP_401_UNAUTHORIZED)
        if token_type != AppRefreshToken().access_token.token_type:
            return Response({'error': 'Wrong token_type'}, status=status.HTTP_401_UNAUTHORIZED)

        # Exp_time проверяется в decode
        if App.objects.filter(id=app_id).exists():
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenForApp(APIView):
    """
    Рефреш токена для приложения
    """
    authentication_classes = ()

    def post(self, request: Request):
        try:
            token = request.data['refresh']
        except KeyError:
            return Response({'error': 'Field "refresh" is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = token_backend.decode(token)
        except (InvalidTokenError, TokenBackendError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            token_type = payload['token_type']
        except KeyError:
            return Response({'error': 'No token_type for token was given'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            app_id = payload['id']
        except KeyError:
            return Response({'error', 'No id in token'}, status=status.HTTP_401_UNAUTHORIZED)
        if token_type != AppRefreshToken.token_type:
            return Response({'error': 'Wrong token_type'}, status=status.HTTP_401_UNAUTHORIZED)

        # Exp_time проверяется в decode
        if not App.objects.filter(id=app_id).exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        refresh = AppRefreshToken(token=token, verify=False)
        data = {
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)
