from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Pet

@receiver(post_save, sender=Pet)
def update_profile_points_on_pet_change(sender, instance, **kwargs):
    """
    Update the owner's profile points when a pet's points change
    """
    instance.owner.profile.update_points()

@receiver(post_delete, sender=Pet)
def update_profile_points_on_pet_delete(sender, instance, **kwargs):
    """
    Update the owner's profile points when a pet is deleted
    """
    instance.owner.profile.update_points()