"""
This module is a Django management command that clears the Badge from the database
"""
from django.core.management.base import BaseCommand
from users.models import Badge


class Command(BaseCommand):
    """
    This class is a Django management command that clears the Feature data from the database
    """
    help = "Clear the Badge data from the database"

    def handle(self, *args, **kwargs) -> None:
        """
        This function clears the badge data from the database

        :param args: None expected
        :param kwargs: None expected
        :return: None
        """
        Badge.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Cleared the Badge data"))

