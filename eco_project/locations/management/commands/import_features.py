"""
This script imports features from a file into the database.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import os
import sys
from random import choice

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from locations.models import (
    FeatureType,
    FeatureInstance,
    QuestionAnswer,
    QuestionFeature,
    LocationsAppSettings,
)
from locations.signals import update_feature_instance_qr_code


def get_img_ext(base_dir, extra) -> str:
    """
    Get the extension of the image file

    :param base_dir: The base directory of the image file
    :param extra: The extra data to get the extension from
    :return: The extension of the image file
    """

    return os.path.join(base_dir, "images", extra[0] if extra else "").split(".")[-1]


def random_letters(length: int = 5) -> str:
    """
    Return a random string of letters and numbers of a given length.

    :param length: The length of the random string (default 5)
    :return: The random string
    """
    return "".join(choice("1234567890ABCDEF") for _ in range(length))


class Command(BaseCommand):
    """
    This script is used to import feature instance and type data into the database.
    """

    help = "Import 3D map chunk data into the database"

    def handle(self, *args, **kwargs) -> None:
        """
        Handle the command to import feature instance and type data into the database.

        :param args: None
        :param kwargs: None
        :return: None
        """
        # Disconnect the QR code update signal to prevent it from running on every save.
        post_save.disconnect(update_feature_instance_qr_code, sender=FeatureInstance)
        post_save.disconnect(update_feature_instance_qr_code, sender=LocationsAppSettings)

        self.import_feature_types()
        self.import_feature_instances()
        self.import_feature_questions()

        # Reconnect the signal so that it can trigger again
        post_save.connect(update_feature_instance_qr_code, sender=FeatureInstance)
        self.stdout.write(self.style.SUCCESS("Starting saving QR codes"))
        update_feature_instance_qr_code(
            sender=LocationsAppSettings,
            instance=LocationsAppSettings.get_instance(),
            progress_bar=True
        )
        post_save.connect(update_feature_instance_qr_code, sender=FeatureInstance)
        self.stdout.write(self.style.SUCCESS("Saved QR codes to database"))

    def _read_clean_lines(self, file_path: str) -> list:
        """
        Read the lines from a file and remove any empty lines or comments.

        :param file_path: The path to the file to read
        :return: The cleaned lines from the file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # read, then clean lines before returning
                return [line.strip() for line in f.readlines()
                        if line.strip() and not line.strip().startswith("#")]
        except FileNotFoundError:
            # If the file is not found, print an error message and return an empty list
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return []

    def _process_feature_type_line(self, line: str, base_dir: str) -> bool:
        """
        Process one line of feature type data and save it to the database.

        :param line: The line of data to process
        :param base_dir: The base directory of the image and mesh files
        :return: True if the data was saved successfully, False otherwise
        """

        # get the data from the line
        name, description, colour, image_file, mesh_file = [data.strip() for data in
                                                            line.split(",")]

        # check image exists
        if not (os.path.exists(os.path.join(base_dir, "images", image_file)) and
                os.path.isfile(os.path.join(base_dir, "images", image_file))):
            self.stdout.write(self.style.ERROR("Image does not exist"))
            sys.exit()
        img_extension = os.path.join(base_dir, "images", image_file).split(".")[-1]

        # save it to the database
        with open(os.path.join(base_dir, "images", image_file), "rb") as f:
            img_file = default_storage.save(f"locations/feature_type_img/"
                                            f"{name}{random_letters()}.{img_extension}",
                                            File(f))

        # save mesh to the db if it exists
        mesh_saved = None
        if bool(mesh_file):
            with open(os.path.join(base_dir, "meshes", mesh_file) if bool(mesh_file) else "",
                      "rb") as f:
                mesh_saved = default_storage.save(f"locations/feature_mesh/"
                                                  f"{name}{random_letters()}.glb", File(f))
        feature = FeatureType(name=name, description=description, colour=colour,
                              generic_img=img_file)
        if bool(mesh_file):
            feature.feature_mesh = mesh_saved
        feature.save()
        return True

    def import_feature_types(self) -> None:
        """
        Import the generic feature types from a text file.

        :return: None
        """
        # open the file and read the lines
        base_dir = os.path.join(os.getcwd(), "locations/management/commands/feature_data")
        file_path = os.path.join(base_dir, "feature_types.txt")

        lines = self._read_clean_lines(file_path)

        successes = 0
        for line in lines:  # process each feature type line by line
            if self._process_feature_type_line(line, base_dir):
                successes += 1

        self.stdout.write(self.style.SUCCESS(f"Saved {successes} feature type(s) to database"))

    def _process_feature_instance_line(self, line: str, base_dir: str) -> bool:
        """
        Process one line of feature instance data and save it to the database.

        :param line: The line of data to process
        :param base_dir: The base directory of the image files
        :return: True if the data was saved successfully, False otherwise
        """

        # check data given is valid
        if len(line.split(",")) < 5:
            self.stdout.write(self.style.ERROR(f"Invalid instance line (not enough data): {line}"))
            return False

        # get the data from the line
        (instance_name, general_type_name,
         slug, lat_str, lon_str, *extra) = [x.strip() for x in line.split(",")]

        # import lat and long
        try:
            latitude, longitude = float(lat_str), float(lon_str)
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid latitude/"
                                               f"longitude for instance {instance_name}"))
            return False

        # get the feature type
        try:
            feature = FeatureType.objects.get(name=general_type_name)
        except FeatureType.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"FeatureType '{general_type_name}' does not exist for instance {instance_name}"
            ))
            return False

        # check if there is a specific image file for this feature
        specific_img_file = None
        if extra[0] if extra else "":
            if not (os.path.exists(os.path.join(base_dir, "images", extra[0] if extra else "")) and
                    os.path.isfile(os.path.join(base_dir, "images", extra[0] if extra else ""))):
                self.stdout.write(self.style.ERROR(
                    f"Image does not exist for instance {instance_name}"
                ))
                return False

            with open(os.path.join(base_dir, "images", extra[0] if extra else ""), "rb") as f:
                specific_img_file = default_storage.save(
                    (f"locations/feature_instance_img/{instance_name}"
                     f"{random_letters()}.{get_img_ext(base_dir, extra)}"), File(f))

        # save the instance to the database
        instance = FeatureInstance(
            name=instance_name,
            slug=slug,
            feature=feature,
            latitude=latitude,
            longitude=longitude,
        )
        if specific_img_file:
            instance.specific_img = specific_img_file
        instance.save()
        return True

    def import_feature_instances(self) -> None:
        """
        Import the feature instances from a text file into the database.

        :return: None
        """
        base_dir = os.path.join(os.getcwd(), "locations/management/commands/feature_data")
        file_path = os.path.join(base_dir, "feature_instances.txt")

        lines = self._read_clean_lines(file_path)

        # process each feature instance line by line
        for line in lines:
            self._process_feature_instance_line(line, base_dir)

        self.stdout.write(self.style.SUCCESS("Saved feature instances to database"))

    def _process_feature_question_line(self, line: str) -> bool:
        """
        Process one line of question feature data and save it to the database.

        :param line: the line of data to process
        :return: True if the data was saved successfully, False otherwise
        """

        fields = [field.strip() for field in line.split(",")]  # split up fields

        if len(fields) < 6:  # check if there is enough data
            self.stdout.write(self.style.ERROR(f"Not enough data in line: {line}"))
            return False

        # get data from fields
        question_text, feature_instance_slug = fields[0], fields[1]
        case_sensitive = fields[2].lower() == "true"

        # check fuzzy data is right
        use_fuzzy_comparison = fields[3].lower() == "true"
        try:
            fuzzy_threshold = int(fields[4])
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid fuzzy threshold '"
                                               f"{fields[4]}' in line: {line}"))
            return False
        if not 0 <= fuzzy_threshold <= 100:
            self.stdout.write(self.style.ERROR(
                f"Fuzzy threshold must be between 0 and 100, not {fuzzy_threshold} in line: {line}"
            ))
            return False

        # import the choices for the answers
        answer_choices = fields[5:]
        try:
            feature_instance = FeatureInstance.objects.get(slug=feature_instance_slug)
        except FeatureInstance.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"FeatureInstance with slug '{feature_instance_slug}'"
                f" not found for question: {question_text}"
            ))
            return False

        # Save the question feature to the database
        question_feature = QuestionFeature(
            question_text=question_text,
            feature=feature_instance,
            case_sensitive=case_sensitive,
            use_fuzzy_comparison=use_fuzzy_comparison,
            fuzzy_threshold=fuzzy_threshold,
        )
        question_feature.save()
        for answer in answer_choices:
            if answer:
                QuestionAnswer.objects.create(question=question_feature, choice_text=answer)
        return True

    def import_feature_questions(self) -> None:
        """
        Import the feature questions from a text file into the database.

        :return: None
        """
        base_dir = os.path.join(os.getcwd(), "locations/management/commands/feature_data")
        file_path = os.path.join(base_dir, "feature_questions.txt")

        # Read in all the lines from the file
        lines = self._read_clean_lines(file_path)
        successes = 0
        for line in lines: # go through each line and import each one
            if self._process_feature_question_line(line):
                successes += 1
        self.stdout.write(self.style.SUCCESS(f"Saved {successes} question feature(s) to database"))
