"""
This file contains signals that are triggered when a User is created or saved.
These signals are used to create a Profile instance for each new User
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This function is called whenever a new User is created, it creates a Profile instance and
    associates it with the new User.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensures that on each save the user has a profile, ie it hasn't been deleted.
    If no profile exists, creates one.
    """
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates a Profile if one doesn't exist,
    and then saves it.
    """
    profile, was_created = Profile.objects.get_or_create(user=instance)
    # Optionally, do any additional updates to profile here
    profile.save()