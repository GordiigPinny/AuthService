from rest_framework import serializers
from Apps.models import App


class AppSerializer(serializers.ModelSerializer):
    """
    Сериализатор приложения
    """
    id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    secret = serializers.CharField(required=True, allow_null=False, allow_blank=False, write_only=True)

    class Meta:
        model = App
        fields = [
            'id',
            'secret',
        ]

    def create(self, validated_data):
        new = App.objects.create(id=validated_data['id'], secret=validated_data['secret'])
        return new
