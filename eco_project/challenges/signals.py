"""
Signals for the challenges app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
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

    @param sender: The sender of the signal
    @param instance: The instance of the sender
    @param created: Whether the instance was created or updated
    @param kwargs: Additional keyword
    @return: None
    """
    if created:
        # Automatically create a Streak record for the new user
        Streak.objects.create(user=instance)
