"""
This module is a Django management command that clears the Badge from the database

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
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

        @param args: None expected
        @param kwargs: None expected
        @return: None
        """
        Badge.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Cleared the Badge data"))
