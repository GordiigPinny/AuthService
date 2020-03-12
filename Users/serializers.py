from django.contrib.auth.models import User
from rest_framework import serializers


class UserListSerializer(serializers.ModelSerializer):
    """
    Сериализатор спискового представления юзера
    """
    profile_pic_link = serializers.URLField(source='userext.profile_pic_link')
    is_moderator = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'profile_pic_link',
            'is_superuser',
            'is_moderator',
        ]

    def get_is_moderator(self, instance: User):
        return instance.userext.is_moderator()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор юзера
    """
    pin_sprite = serializers.IntegerField(source='userext.pin_sprite')
    created_dt = serializers.DateTimeField(source='userext.created_dt')
    geopin_sprite = serializers.IntegerField(source='userext.geopin_sprite')
    unlocked_pins = serializers.SerializerMethodField()
    unlocked_geopins = serializers.SerializerMethodField()
    rating = serializers.CharField(source='userext.rating')
    profile_pic_link = serializers.URLField(source='userext.profile_pic_link')
    is_moderator = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'pin_sprite',
            'geopin_sprite',
            'unlocked_pins',
            'unlocked_geopins',
            'rating',
            'profile_pic_link',
            'created_dt',
            'is_superuser',
            'is_moderator',
        ]

    def get_unlocked_pins(self, instance: User):
        return [int(x) for x in instance.userext.unlocked_pins.split(',')]

    def get_unlocked_geopins(self, instance: User):
        return [int(x) for x in instance.userext.unlocked_geopins.split(',')]

    def get_is_moderator(self, instance: User):
        return instance.userext.is_moderator()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рекистрации пользователя
    """
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        new = User.objects.create(username=validated_data['username'], email=validated_data.get('email', ''))
        new.set_password(validated_data['password'])
        new.save()
        return new
