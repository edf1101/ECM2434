"""
This module is a Django management command that clears the 3D map chunk data from the database
and the media folder.
"""
from django.core.management.base import BaseCommand
from locations.models import Map3DChunk
from mysite.settings import MEDIA_ROOT
import os
from typing import Any

import json  # If reading from a file


class Command(BaseCommand):
    """
    This class is a Django management command that clears the 3D map chunk data from the database
    """
    help = "Import 3D map chunk data into the database"

    def handle(self, *args, **kwargs) -> None:
        """
        This function clears the 3D map chunk data from the database

        :param args: None expected
        :param kwargs: None expected
        :return: None
        """

        # clear the media 3d_map_chunks folder
        folder = os.path.join(MEDIA_ROOT, 'locations/3d_map_chunks')

        # Check if the folder exists
        if os.path.exists(folder):
            # Remove everything in the folder
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        Map3DChunk.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f"Cleared the chunk data"))
