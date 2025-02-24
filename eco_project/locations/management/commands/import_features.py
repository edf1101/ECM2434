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


class Command(BaseCommand):
    """
    This script is used to import feature instance and type data into the database.
    """

    help = "Import 3D map chunk data into the database"

    def handle(self, *args, **kwargs) -> None:
        """
        This function is called when the import_features script is run.

        @param args:  None expected
        @param kwargs: None expected
        @return: None
        """
        # Disconnect the QR code update signal to prevent it from running on
        # every save.
        post_save.disconnect(
            update_feature_instance_qr_code,
            sender=FeatureInstance)
        post_save.disconnect(
            update_feature_instance_qr_code, sender=LocationsAppSettings
        )

        self.import_feature_types()
        self.import_feature_instances()
        self.import_feature_questions()

        # Reconnect the signal so that it can trigger again
        post_save.connect(
            update_feature_instance_qr_code,
            sender=FeatureInstance)

        # Now trigger an update of QR codes for all FeatureInstances.
        update_feature_instance_qr_code(
            sender=LocationsAppSettings,
            instance=LocationsAppSettings.get_instance())
        post_save.connect(
            update_feature_instance_qr_code,
            sender=FeatureInstance)

    def import_feature_types(self) -> None:
        """
        Import the generic feature types from the file.

        @return: None
        """

        # read lines from the file
        folder = os.path.join(
            os.getcwd(),
            "locations/management/commands/feature_data")
        image_dir = os.path.join(folder, "images")
        mesh_dir = os.path.join(folder, "meshes")
        file_dir = os.path.join(folder, "feature_types.txt")

        lines = []
        with open(file_dir, "r", encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            lines = [line for line in lines if (line != "" and line[0] != "#")]
        successes = 0
        for line in lines:
            split_data = line.split(",")
            split_data = [data.strip() for data in split_data]
            name = split_data[0]
            description = split_data[1]
            colour = split_data[2]
            image_path = split_data[3]
            mesh_path = split_data[4]
            using_mesh = mesh_path != ""

            # check image exists
            image_path = os.path.join(image_dir, image_path)
            if not os.path.exists(
                    image_path) or not os.path.isfile(image_path):
                self.stdout.write(
                    self.style.ERROR(f"Image {image_path} does not exist")
                )
                sys.exit()
            img_extension = image_path.split(".")[-1]
            # check mesh exists
            mesh_path = os.path.join(mesh_dir, mesh_path)
            if using_mesh and (
                    not os.path.exists(mesh_path) or not os.path.isfile(image_path)
            ):
                self.stdout.write(
                    self.style.ERROR(f"Mesh {mesh_path} does not exist"))
                sys.exit()

            # create some random letters for end of the filename to avoid
            # duplicates
            random_letters = "".join(
                [choice("1234567890ABCDEF") for i in range(5)])

            # create image file
            mesh_file = None

            with open(image_path, "rb") as f:
                file = File(f)  # Create a Django file object

                # Save it with a safe path so that unsafe error isn't raised
                img_file = default_storage.save(
                    f"locations/feature_type_img/{name}{random_letters}.{img_extension}", file, )
            if using_mesh:
                with open(mesh_path, "rb") as f:
                    file = File(f)
                    mesh_file = default_storage.save(
                        f"locations/feature_mesh/{name}{random_letters}.glb", file)

            # actually create the object
            feature = FeatureType(
                name=name,
                description=description,
                colour=colour,
                generic_img=img_file)
            if using_mesh:
                feature.feature_mesh = mesh_file

            feature.save()
            successes += 1

        self.stdout.write(
            self.style.SUCCESS(f"Saved {successes} feature type to database")
        )

    def import_feature_instances(self) -> None:
        """
        Import feature instances from a text file.
        """
        # Set up directories
        base_dir = os.path.join(
            os.getcwd(), "locations/management/commands/feature_data"
        )
        image_dir = os.path.join(base_dir, "images")
        file_path = os.path.join(base_dir, "feature_instances.txt")

        # Read and filter lines from file
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return

        # clean up the lines
        lines = [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]

        successes = 0
        for line in lines:
            # Split by comma and strip whitespace from each entry
            split_data = [data.strip() for data in line.split(",")]
            # Ensure we have at least 5 elements (img filename is optional)
            if len(split_data) < 5:
                self.stdout.write(
                    self.style.ERROR(f"Invalid line (not enough data): {line}")
                )
                continue

            # Unpack the fields
            instance_name = split_data[0]
            general_type_name = split_data[1]
            slug = split_data[2]
            lat_str = split_data[3]
            lon_str = split_data[4]
            img_filename = split_data[5] if len(split_data) > 5 else ""

            # Convert latitude and longitude
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        f"Invalid latitude/longitude for instance {instance_name}"
                    )
                )
                continue

            # Retrieve the related FeatureType by its name
            try:
                feature = FeatureType.objects.get(name=general_type_name)
            except FeatureType.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"FeatureType with name '{general_type_name}' "
                        f"does not exist for instance {instance_name}"
                    )
                )
                continue

            # Handle the instance-specific image if provided
            specific_img_file = None
            if img_filename:
                full_img_path = os.path.join(image_dir, img_filename)
                if not os.path.exists(full_img_path) or not os.path.isfile(
                        full_img_path
                ):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Image {full_img_path} does not exist for instance {instance_name}"
                        )
                    )
                    continue

                img_extension = full_img_path.split(".")[-1]
                random_letters = "".join(
                    choice("1234567890ABCDEF") for _ in range(5))
                # Construct a safe storage path for the image
                storage_path = (
                    f"locations/feature_instance_img/"
                    f"{instance_name}{random_letters}.{img_extension}"
                )

                with open(full_img_path, "rb") as f:
                    file_obj = File(f)
                    specific_img_file = default_storage.save(
                        storage_path, file_obj)

            # Create and save the FeatureInstance
            feature_instance = FeatureInstance(
                name=instance_name,
                slug=slug,
                feature=feature,
                latitude=latitude,
                longitude=longitude,
            )
            if specific_img_file:
                feature_instance.specific_img = specific_img_file

            feature_instance.save()
            successes += 1

        self.stdout.write(self.style.SUCCESS(
            f"Saved {successes} feature instances to database"))

    def import_feature_questions(self) -> None:
        """
        Import question and answer data for feature instances from a text file.
        """
        # Define the directory and file path
        base_dir = os.path.join(
            os.getcwd(), "locations/management/commands/feature_data"
        )
        file_path = os.path.join(base_dir, "feature_questions.txt")

        # Read the file
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return

        # clean up the read lines data
        lines = [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]

        successes = 0

        for line in lines:
            # Split the line into fields.
            fields = [field.strip() for field in line.split(",")]
            if len(fields) < 6:
                self.stdout.write(
                    self.style.ERROR(f"Not enough data in line: {line}"))
                continue

            # Unpack fields
            question_text = fields[0]
            feature_instance_slug = fields[1]
            case_sensitive_str = fields[2]
            use_fuzzy_str = fields[3]
            fuzzy_threshold_str = fields[4]
            answer_choices = fields[5:]  # remaining fields are answers

            # Convert booleans from strings
            case_sensitive = case_sensitive_str.lower() == "true"
            use_fuzzy_comparison = use_fuzzy_str.lower() == "true"

            # Convert fuzzy threshold to an integer and error check
            try:
                fuzzy_threshold = int(fuzzy_threshold_str)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        f"Invalid fuzzy threshold '{fuzzy_threshold_str}' in line: {line}"
                    )
                )
                continue
            if fuzzy_threshold < 0 or fuzzy_threshold > 100:
                self.stdout.write(
                    self.style.ERROR(
                        f"Fuzzy threshold must be between 0 and 100, not {fuzzy_threshold} "
                        f"in line: {line}"))
                continue

            # Get FeatureInstance object by slug
            try:
                feature_instance = FeatureInstance.objects.get(
                    slug=feature_instance_slug
                )
            except FeatureInstance.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"FeatureInstance with slug '{feature_instance_slug}'"
                        f" not found for question: {question_text}"
                    )
                )
                continue

            # Create the QuestionFeature object and add in the data
            question_feature = QuestionFeature(
                question_text=question_text,
                feature=feature_instance,
                case_sensitive=case_sensitive,
                use_fuzzy_comparison=use_fuzzy_comparison,
                fuzzy_threshold=fuzzy_threshold,
            )
            question_feature.save()

            # Create a QuestionAnswer object for each answer provided
            for answer in answer_choices:
                if answer:  # ensure that the answer is not an empty string
                    question_answer = QuestionAnswer(
                        question=question_feature, choice_text=answer
                    )
                    question_answer.save()

            successes += 1

        self.stdout.write(self.style.SUCCESS(
            f"Saved {successes} question features to database"))
