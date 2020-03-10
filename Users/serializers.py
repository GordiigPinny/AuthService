from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор юзера
    """
    pin_sprite = serializers.IntegerField(source='userext.pin_sprite')
    geopin_sprite = serializers.IntegerField(source='userext.geopin_sprite')
    unlocked_pins = serializers.SerializerMethodField()
    unlocked_geopins = serializers.SerializerMethodField()
    rating = serializers.CharField(source='userext.rating')
    profile_pic_link = serializers.URLField(source='userext.profile_pic_link')

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
        ]

    def get_unlocked_pins(self, instance: User):
        return [int(x) for x in instance.userext.unlocked_pins.split(',')]

    def get_unlocked_geopins(self, instance: User):
        return [int(x) for x in instance.userext.unlocked_geopins.split(',')]


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
        new = User.objects.create(username=validated_data['username'], email=validated_data['email'])
        new.set_password(validated_data['password'])
        new.save()
        return new
