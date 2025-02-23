"""
This command updates all user profile points based on their pets.
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
        users = User.objects.all()
        updated = 0
        for user in users:
            user.profile.update_points()
            updated += 1
        self.stdout.write(f"Updated points for {updated} profiles")
