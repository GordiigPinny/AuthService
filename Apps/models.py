from django.db import models
from django.contrib.auth.models import User


class App(models.Model):
    """
    Модель для приложения
    """
    id = models.CharField(null=False, blank=False, max_length=256, primary_key=True)
    secret = models.CharField(null=False, blank=False, max_length=512)
    created_by = models.ForeignKey(User, related_name='created_apps', null=True, on_delete=models.CASCADE)
    is_internal = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return f'{self.id}'
