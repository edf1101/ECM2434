# lootboxes/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import LootBox

User = get_user_model()

@receiver(post_save, sender=LootBox)
def update_user_points(sender, instance, created, **kwargs):
    """
    Signal handler to update user's points after a loot box spin.
    """
    if not created:
        return

    profile = instance.user.profile  # Access the profile linked to the user
    result = instance.spin()  # Spin the lootbox and get the result message
    new_points = profile.points  # Get the updated points

    # Update the points in the Profile model
    profile.points = new_points
    profile.save()

    return result
