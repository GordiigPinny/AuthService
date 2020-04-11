from rest_framework import serializers
from Apps.models import App


class AppSerializer(serializers.ModelSerializer):
    """
    Сериализатор приложения
    """
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    secret = serializers.CharField(required=True, allow_null=False, allow_blank=False, write_only=True)

    class Meta:
        model = App
        fields = [
            'name',
            'secret',
        ]

    def create(self, validated_data):
        new = App.create_app_secured(validated_data['name'], validated_data['secret'])
        return new
