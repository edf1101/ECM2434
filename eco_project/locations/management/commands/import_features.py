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

    @param base_dir: The base directory of the image file
    @param extra: The extra data to get the extension from
    @return: The extension of the image file
    """

    return os.path.join(base_dir, "images", extra[0] if extra else "").split(".")[-1]


class Command(BaseCommand):
    """
    This script is used to import feature instance and type data into the database.
    """

    help = "Import 3D map chunk data into the database"

    def handle(self, *args, **kwargs) -> None:
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
        """Read a file and return a list of cleaned lines (ignoring blank lines and comments)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines()
                        if line.strip() and not line.strip().startswith("#")]
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return []

    def _random_letters(self, length: int = 5) -> str:
        """Return a random string of letters and digits of given length."""
        return "".join(choice("1234567890ABCDEF") for _ in range(length))

    def _process_feature_type_line(self, line: str, base_dir: str) -> bool:
        """Process one line of feature type data and save it to the database."""

        name, description, colour, image_file, mesh_file = [data.strip() for data in
                                                            line.split(",")]
        if not (os.path.exists(os.path.join(base_dir, "images", image_file)) and
                os.path.isfile(os.path.join(base_dir, "images", image_file))):
            self.stdout.write(self.style.ERROR("Image does not exist"))
            sys.exit()
        img_extension = os.path.join(base_dir, "images", image_file).split(".")[-1]

        with open(os.path.join(base_dir, "images", image_file), "rb") as f:
            img_file = default_storage.save(f"locations/feature_type_img/"
                                            f"{name}{self._random_letters()}.{img_extension}",
                                            File(f))
        mesh_saved = None
        if bool(mesh_file):
            with open(os.path.join(base_dir, "meshes", mesh_file) if bool(mesh_file) else "",
                      "rb") as f:
                mesh_saved = default_storage.save(f"locations/feature_mesh/"
                                                  f"{name}{self._random_letters()}.glb", File(f))
        feature = FeatureType(name=name, description=description, colour=colour,
                              generic_img=img_file)
        if bool(mesh_file):
            feature.feature_mesh = mesh_saved
        feature.save()
        return True

    def import_feature_types(self) -> None:
        """Import the generic feature types from the file."""
        base_dir = os.path.join(os.getcwd(), "locations/management/commands/feature_data")
        file_path = os.path.join(base_dir, "feature_types.txt")
        lines = self._read_clean_lines(file_path)
        successes = 0
        for line in lines:
            if self._process_feature_type_line(line, base_dir):
                successes += 1
        self.stdout.write(self.style.SUCCESS(f"Saved {successes} feature type(s) to database"))

    def _process_feature_instance_line(self, line: str, base_dir: str) -> bool:
        """Process one line of feature instance data and save it to the database."""
        if len(line.split(",")) < 5:
            self.stdout.write(self.style.ERROR(f"Invalid instance line (not enough data): {line}"))
            return False

        (instance_name, general_type_name,
         slug, lat_str, lon_str, *extra) = [x.strip() for x in line.split(",")]
        try:
            latitude, longitude = float(lat_str), float(lon_str)
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid latitude/"
                                               f"longitude for instance {instance_name}"))
            return False

        try:
            feature = FeatureType.objects.get(name=general_type_name)
        except FeatureType.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"FeatureType '{general_type_name}' does not exist for instance {instance_name}"
            ))
            return False

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
                     f"{self._random_letters()}.{get_img_ext(base_dir, extra)}"), File(f))

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
        """Import feature instances from a text file."""
        base_dir = os.path.join(os.getcwd(), "locations/management/commands/feature_data")
        file_path = os.path.join(base_dir, "feature_instances.txt")
        lines = self._read_clean_lines(file_path)
        for line in lines:
            self._process_feature_instance_line(line, base_dir)
        self.stdout.write(self.style.SUCCESS("Saved feature instances to database"))

    def _process_feature_question_line(self, line: str) -> bool:
        """Process one line of feature question data and save it to the database."""
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 6:
            self.stdout.write(self.style.ERROR(f"Not enough data in line: {line}"))
            return False

        question_text, feature_instance_slug = fields[0], fields[1]
        case_sensitive = fields[2].lower() == "true"
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
        answer_choices = fields[5:]
        try:
            feature_instance = FeatureInstance.objects.get(slug=feature_instance_slug)
        except FeatureInstance.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"FeatureInstance with slug '{feature_instance_slug}'"
                f" not found for question: {question_text}"
            ))
            return False

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
        """Import question and answer data for feature instances from a text file."""
        base_dir = os.path.join(os.getcwd(), "locations/management/commands/feature_data")
        file_path = os.path.join(base_dir, "feature_questions.txt")
        lines = self._read_clean_lines(file_path)
        successes = 0
        for line in lines:
            if self._process_feature_question_line(line):
                successes += 1
        self.stdout.write(self.style.SUCCESS(f"Saved {successes} question feature(s) to database"))
