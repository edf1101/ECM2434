"""
Signals for the challenges app.
"""

from django.contrib.auth import get_user_model

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Streak


# pylint: disable=unused-argument
@receiver(post_save, sender=get_user_model())
def create_user_streak(sender, instance, created, **kwargs):
    """
    Automatically create a Streak record for the new user if one does not already exist.
    """
    if created:
        # Automatically create a Streak record for the new user
        Streak.objects.create(user=instance)
