from django.db import models


class App(models.Model):
    """
    Модель для приложения
    """
    id = models.CharField(null=False, blank=False, max_length=256, primary_key=True)
    secret = models.CharField(null=False, blank=False, max_length=512)

    def __str__(self):
        return f'{self.id}'
