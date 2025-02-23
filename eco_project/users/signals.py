"""
This file contains signals that are triggered when a User is created or saved.
These signals are used to create a Profile instance for each new User

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


# pylint: disable=unused-argument
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs) -> None:
    """
    Creates a Profile if one doesn't exist,
    and then saves it.

    @param sender: The sender of the signal
    @param instance: The instance of the sender
    @param created: Whether the instance was created
    @param kwargs: Additional keyword arguments
    @return: None
    """
    profile, _ = Profile.objects.get_or_create(user=instance)
    profile.save()
