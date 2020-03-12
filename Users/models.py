from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list


class UserExt(models.Model):
    """
    Дополнение к стандартному классу User
    """
    NEWBIE, CURIOUS, EXPLORER, COLUMB = 'н', 'л', 'и', 'к'
    RATING_CHOICES = (
        (NEWBIE,    'Новичок'),
        (CURIOUS,   'Любопытный'),
        (EXPLORER,  'Исследователь'),
        (COLUMB,    'Колумб'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    pin_sprite = models.BigIntegerField(default=1, null=False)
    geopin_sprite = models.BigIntegerField(default=1, null=False)
    unlocked_pins = models.TextField(blank=True, null=False, default='1',
                                     validators=[validate_comma_separated_integer_list])
    unlocked_geopins = models.TextField(blank=True, null=False, default='1',
                                        validators=[validate_comma_separated_integer_list])
    achievements = models.TextField(blank=True, null=False, default='',
                                    validators=[validate_comma_separated_integer_list])
    rating = models.CharField(choices=RATING_CHOICES, null=False, default=NEWBIE, max_length=2)
    profile_pic_link = models.URLField(null=True, blank=True)

    def is_moderator(self):
        return self.user.groups.filter(name='moderators').exists()

    def __str__(self):
        return f'{self.user.username} ext'
