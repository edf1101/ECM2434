"""
This file contains signals that are triggered when a User is created or saved.
These signals are used to create a Profile instance for each new User
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates a Profile if one doesn't exist,
    and then saves it.
    """
    profile, was_created = Profile.objects.get_or_create(user=instance)
    profile.save()
