from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import Response, Request, APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.exceptions import TokenBackendError
from jwt.exceptions import InvalidTokenError
from Users.permissions import IsAuthenticated
from Apps.models import App
from Apps.serializers import AppSerializer
from OAuth.tokens import ThirdPartyAppRefreshToken


class OAuthAppsView(ListCreateAPIView):
    """
    Вьюха для списка и создания приложения
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = AppSerializer

    def get_queryset(self):
        return App.objects.filter(created_by=self.request.user)

    def post(self, request: Request, *args, **kwargs):
        s = AppSerializer(data=request.data)
        if s.is_valid():
            app = s.save()
            app.created_by = self.request.user
            app.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenPairForThirdPartyApp(APIView):
    """
    Возврат токенов по client_id, client_secret, username, password
    """
    authentication_classes = ()

    def post(self, request: Request):
        client_id = request.data.get('client_id', None)
        client_secret = request.data.get('client_secret', None)
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        try:
            app = App.objects.get(id=client_id, secret=client_secret, is_internal=False)
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise User.DoesNotExist
        except App.DoesNotExist:
            return Response({'error': 'Wrong client credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Wrong user credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        token = ThirdPartyAppRefreshToken.for_user(user)
        token['client_id'] = client_id
        data = {
            'access': str(token.access_token),
            'refresh': str(token),
        }
        return Response(data, status=status.HTTP_200_OK)


class OAuthTokenRefreshView(APIView):
    """
    Рефреш токена для oauth
    """
    authentication_classes = ()

    def post(self, request: Request):
        try:
            token = request.data['refresh']
        except KeyError:
            return Response({'error': 'Field "refresh" is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            username = request.data['username']
        except KeyError:
            return Response({'error': 'Field "username" is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            req_client_id = request.data['client_id']
        except KeyError:
            return Response({'error': 'Field "client_id" is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = token_backend.decode(token)
        except (InvalidTokenError, TokenBackendError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            token_type = payload['token_type']
        except KeyError:
            return Response({'error': 'No token_type for token was given'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = payload['id']
        except KeyError:
            return Response({'error', 'No id in token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            client_id = payload['client_id']
        except KeyError:
            return Response({'error', 'No client_id in token'}, status=status.HTTP_401_UNAUTHORIZED)
        if token_type != ThirdPartyAppRefreshToken.token_type:
            return Response({'error': 'Wrong token_type'}, status=status.HTTP_401_UNAUTHORIZED)

        # Exp_time проверяется в decode
        if not App.objects.filter(id=client_id).exists() or not User.objects.filter(id=user_id).exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if req_client_id != client_id:
            return Response({'error': 'Client ids don\'t match'}, status=status.HTTP_401_UNAUTHORIZED)

        if User.objects.get(id=user_id).username != username:
            return Response({'error': 'Username is wrong for given token'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = ThirdPartyAppRefreshToken(token=token, verify=False)
        data = {
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)
