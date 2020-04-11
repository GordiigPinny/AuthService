from django.db import models
from django.contrib.auth.hashers import make_password


class App(models.Model):
    """
    Модель для приложения
    """
    name = models.CharField(null=False, blank=False, max_length=256, primary_key=True)
    secret = models.CharField(null=False, blank=False, max_length=512)

    @staticmethod
    def create_app_secured(name, secret):
        return App.objects.create(name=name, secret=make_password(secret))

    def __str__(self):
        return f'{self.name}'

    def set_secret(self, secret):
        self.secret = make_password(secret)
