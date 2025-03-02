"""
This module is a Django management command that clears the 3D map chunk data from the database
and the media folder.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import os

from django.core.management.base import BaseCommand
from locations.models import FeatureType, FeatureInstance, QuestionFeature
from mysite.settings import MEDIA_ROOT


class Command(BaseCommand):
    """
    This class is a Django management command that clears the Feature data from the database
    """

    help = "Clear the feature data from the database"

    def handle(self, *args, **kwargs) -> None:
        """
        This function clears the 3D map chunk data from the database

        @param args: None expected
        @param kwargs: None expected
        @return: None
        """

        self.clear_feature_types()
        self.clear_feature_instances()
        self.clear_question_data()
        self.stdout.write(self.style.SUCCESS("Cleared the Feature data"))

    def clear_feature_types(self) -> None:
        """
        Clear the feature types data

        @return: None
        """
        # clear the media feature_type_img folder
        folder = os.path.join(MEDIA_ROOT, "locations/feature_type_img")

        # Check if the folder exists
        if os.path.exists(folder):
            # Remove everything in the folder
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        # clear the media feature_mesh folder
        folder = os.path.join(MEDIA_ROOT, "locations/feature_mesh")

        # Check if the folder exists
        if os.path.exists(folder):
            # Remove everything in the folder
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        FeatureType.objects.all().delete()

    def clear_feature_instances(self) -> None:
        """
        Clear the feature instances data

        @return: None
        """

        # clear the media feature_type_img folder
        folder = os.path.join(MEDIA_ROOT, "locations/feature_instance_img")

        # Check if the folder exists
        if os.path.exists(folder):
            # Remove everything in the folder
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        # clear the media qr_code folder
        folder = os.path.join(MEDIA_ROOT, "locations/qr_codes")

        # Check if the folder exists
        if os.path.exists(folder):
            # Remove everything in the folder
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))

        FeatureInstance.objects.all().delete()

    def clear_question_data(self) -> None:
        """
        Clear the question data from the database

        @return: None
        """
        QuestionFeature.objects.all().delete()
