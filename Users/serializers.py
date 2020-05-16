from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from Users.utils import is_moderator


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор спискового представления юзера
    """
    is_moderator = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_superuser',
            'is_moderator',
        ]

    def get_is_moderator(self, instance: User):
        return is_moderator(instance)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рекистрации пользователя
    """
    username = serializers.CharField(max_length=128, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(required=False, max_length=256, allow_blank=True)
    password = serializers.CharField(allow_null=False, allow_blank=False, min_length=6, max_length=256, write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
        ]

    def create(self, validated_data):
        new = User.objects.create(username=validated_data['username'], email=validated_data.get('email', ''))
        new.set_password(validated_data['password'])
        new.save()
        return new


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Сериализатор формы смены пароля
    """
    password = serializers.CharField(allow_null=False, allow_blank=False, min_length=6, max_length=256, write_only=True)
    password_confirm = serializers.CharField(allow_null=False, allow_blank=False, min_length=6, max_length=256,
                                             write_only=True)
    old_password = serializers.CharField(allow_null=False, allow_blank=False, max_length=256, write_only=True)

    class Meta:
        model = User
        fields = [
            'password',
            'password_confirm',
            'old_password',
        ]

    def update(self, instance: User, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise serializers.ValidationError('Текущий пароль введен неверно')
        if validated_data['password'] != validated_data['password_confirm']:
            raise serializers.ValidationError('Пароли не сходятся')
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
