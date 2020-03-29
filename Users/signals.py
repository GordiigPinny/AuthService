from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group


@receiver(post_save, sender=User)
def add_super_to_moders_group(sender, instance: User, created, **kwargs):
    if not created:
        return
    if not instance.is_superuser:
        return
    g, _ = Group.objects.get_or_create(name='moderators')
    g.user_set.add(instance)
    g.save()
