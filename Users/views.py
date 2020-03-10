from rest_framework import status
from rest_framework.views import APIView, Response, Request
from django.contrib.auth.models import User
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from Users.serializers import RegisterSerializer, UserSerializer


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
