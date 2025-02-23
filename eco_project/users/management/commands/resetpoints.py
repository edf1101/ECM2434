"""
This command updates all user profile points based on their pets.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    This class is a Django management command that updates all user profile points
    based on their pets
    """
    help = "Updates all user profile points based on their pets"

    def handle(self, *args, **kwargs):
        """
        This method updates all user profile points based on their pets
        """
        users = User.objects.all()
        updated = 0
        for user in users:
            user.profile.update_points()
            updated += 1
        self.stdout.write(f"Updated points for {updated} profiles")
