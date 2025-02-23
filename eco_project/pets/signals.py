from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Pet


@receiver(post_save, sender=Pet)
def update_user_points(sender, instance, created, **kwargs):
    profile = instance.owner.profile

    profile.update_points()