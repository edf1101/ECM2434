"""
This module holds the signals for the petReal app.
"""
import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import UserPhoto

@receiver(pre_delete, sender=UserPhoto)
def delete_user_photo_file(sender, instance, **kwargs):
    """
    Deletes the photo file from the media folder when a UserPhoto instance is deleted.
    Using pre_delete so that the file path is still available.
    """

    if instance.photo:
        try:
            file_path = instance.photo.path
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {instance.photo.path}: {e}")