"""
Signals for the pets app.
"""

# pylint: disable=unused-argument

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Pet


@receiver(post_save, sender=Pet)
def update_user_points(sender, instance, created, **kwargs) -> None:
    """
    When the pet is saved, update the user's points.

    @param sender: The sender of the signal
    @param instance: The instance of the model
    @param created: Whether the instance was created or not
    @return: None
    """

    profile = instance.owner.profile

    profile.update_points()
