"""
This module contains tasks to run periodically for the petReal app.
"""
from django.utils import timezone
from .models import UserPhoto


def remove_expired_photos() -> None:
    """
    Deletes expired UserPhoto objects and removes the corresponding image files
    from the media folder.

    @return: None
    """
    now = timezone.now()
    expired_photos = UserPhoto.objects.filter(expiration_date__lte=now)
    for photo in expired_photos:

        if photo.photo:  # Delete the file from storage if it exists
            photo.photo.delete(save=False)

        photo.delete()  # Delete the database record
