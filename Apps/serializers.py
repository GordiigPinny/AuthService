from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from Apps.models import App


class AppSerializer(serializers.ModelSerializer):
    """
    Сериализатор приложения
    """
    id = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                               validators=[UniqueValidator(queryset=App.objects.all())])
    secret = serializers.CharField(required=True, allow_null=False, allow_blank=False, write_only=True)
    created_by = serializers.IntegerField(read_only=True, source='created_by.id')
    is_internal = serializers.BooleanField(read_only=True)

    class Meta:
        model = App
        fields = [
            'id',
            'secret',
            'created_by',
            'is_internal',
        ]

    def create(self, validated_data):
        new = App.objects.create(id=validated_data['id'], secret=validated_data['secret'])
        return new


class AppForTokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для токена
    """
    id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    secret = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        model = App
        fields = [
            'id',
            'secret',
        ]
