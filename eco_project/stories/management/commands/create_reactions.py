"""
This module is a Django management command that creates some story reactions in the database.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import sys

from django.core.management.base import BaseCommand
from stories.models import ReactionType

class Command(BaseCommand):
    """
    This class is a Django management command that creates story reactions in the DB.
    """

    help = "Create story reactions in the database"

    def handle(self, *args, **kwargs) -> None:
        """
        This function creates an Axolotl, Elephant, and Bat in the database.

        :param args: None expected
        :param kwargs: None expected
        :return: None
        """

        # This is a dict of the reaction types that will be created
        reaction_types = [{'name': 'Thumbs Up', 'icon': '👍'},
                          {'name': 'Thumbs Down', 'icon': '👎'},
                          {'name': 'Heart', 'icon': '❤️'},
                          {'name': 'Water', 'icon': '💧'},
                          {'name': 'Tree', 'icon': '🌳'},
                          {'name': 'Elephant', 'icon': '🐘'}]

        # import each one to the DB
        for reaction_type in reaction_types:
            reaction_type_model = ReactionType.objects.create(name=reaction_type['name'],
                                                              icon=reaction_type['icon'])

            reaction_type_model.save()


        sys.stdout.write(self.style.SUCCESS('Successfully created story reactions\n'))
