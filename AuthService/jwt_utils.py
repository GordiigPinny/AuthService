from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class FullInfoTokenPairSerializer(TokenObtainPairSerializer):
    """
    Сериализатор токена юзера со всеми данными
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = FullInfoTokenPairSerializer
