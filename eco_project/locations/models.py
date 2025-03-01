"""
This file contains the models for the locations app.
The models are used to store information about the different types of sustainability features
and their locations.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import os
from typing import Self

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from qrcode import QRCode, constants
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from thefuzz import fuzz


# Create your models here.


class FeatureType(models.Model):
    """
    A model to store a sustainability feature. Ie Recycling bin, water fountain, etc.
    """

    id: models.AutoField = models.AutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField()
    colour = models.CharField(max_length=7,
                              default="#000000")  # Hex colour code
    generic_img: models.ImageField = models.ImageField(
        upload_to="locations/feature_type_img/", blank=False
    )
    feature_mesh = models.FileField(
        upload_to="locations/feature_mesh/", blank=True, null=True
    )

    def __str__(self):
        """
        Returns a string representation of the object.

        @return: The name of the feature.
        """
        return f"{self.name}"


class FeatureInstance(models.Model):
    """
    A model to store a feature type that is specific to a location. Ie a
     recycling bin outside the forum.
    """

    slug = models.SlugField(
        primary_key=True,
        max_length=200,
        unique=True,
        blank=False)
    name = models.CharField(max_length=200, blank=False)
    feature = models.ForeignKey(FeatureType, on_delete=models.CASCADE)
    longitude = models.FloatField()
    latitude = models.FloatField()
    specific_img = models.ImageField(
        upload_to="locations/feature_instance_img/", blank=True, null=True
    )

    qr_code = models.ImageField(
        upload_to="locations/qr_codes/",
        blank=True,
        null=True)

    #pylint: disable=unused-argument
    def update_qr_code(self, skip_signal=False) -> None:
        """
        Updates the QR code for this feature instance.

        @param skip_signal: Whether to skip the signal that triggers this method.
        """
        # Find the absolute path of the static image
        logo_path = finders.find("locations/media/ecopetLogoWhiteBG.png")
        if not logo_path:
            raise FileNotFoundError(
                "Static file 'locations/media/ecopetLogoWhiteBG.png' not found."
            )

        qr = QRCode(error_correction=constants.ERROR_CORRECT_H)
        qr.add_data(
            f"{LocationsAppSettings.get_instance().qr_prefix}{self.slug}")

        # make the image
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=logo_path,  # Use the absolute path from the finder
            color_mask=RadialGradiantColorMask(
                center_color=(74, 107, 66), edge_color=(24, 219, 34)
            ),
            error_correction=constants.ERROR_CORRECT_H,
        )

        qr_code_path = os.path.join(settings.MEDIA_ROOT, "locations/qr_codes/")

        # Create the directory if it doesn't exist
        os.makedirs(qr_code_path, exist_ok=True)
        img_path = os.path.join(qr_code_path, f"{self.slug}.png")
        img.save(img_path)

        # Update the ImageField reference without triggering signals
        self.__class__.objects.filter(pk=self.pk).update(
            qr_code=f"locations/qr_codes/{self.slug}.png"
        )

    @property
    def has_question(self) -> bool:
        """
        Returns whether this feature instance has a question or not.
        """
        return self.questionfeature_set.exists()

    def has_challenge(self) -> bool:
        """
        Returns whether this feature instance has a challenge or not.
        """
        return self.has_question

    def __str__(self):
        """
        Returns a string representation of the object.

        @return: the name of the feature and the slug.
        """
        return f'{self.feature.name} "{self.slug}"'

    @property
    def image(self) -> ImageFieldFile | ImageField:
        """
        Returns specific_img if it exists, otherwise returns the related feature's generic_img.
        """
        if self.specific_img:
            return self.specific_img
        return self.feature.generic_img


class Map3DChunk(models.Model):
    """
    A model to store a 3D map chunk.
    """

    id: models.AutoField = models.AutoField(primary_key=True)
    file: models.FileField = models.FileField(
        upload_to="locations/3d_map_chunks/", blank=False
    )
    file_original_name: models.CharField = models.CharField(
        max_length=200, blank=False)

    # geodesic data
    center_lat: models.FloatField = models.FloatField(blank=False, default=0)
    center_lon: models.FloatField() = models.FloatField(blank=False, default=0)

    bottom_left_lat: models.FloatField = models.FloatField(
        blank=False, default=0)
    bottom_left_lon: models.FloatField() = models.FloatField(blank=False, default=0)

    top_right_lat: models.FloatField = models.FloatField(
        blank=False, default=0)
    top_right_lon: models.FloatField() = models.FloatField(blank=False, default=0)

    # blender data
    bottom_left_x: models.FloatField = models.FloatField(
        blank=False, default=0)
    bottom_left_y: models.FloatField() = models.FloatField(blank=False, default=0)
    bottom_left_z: models.FloatField() = models.FloatField(blank=False, default=0)

    top_right_x: models.FloatField = models.FloatField(blank=False, default=0)
    top_right_y: models.FloatField() = models.FloatField(blank=False, default=0)
    top_right_z: models.FloatField() = models.FloatField(blank=False, default=0)

    def __str__(self):
        """
        Returns a string representation of the object.

        @return: The original file name.
        """
        return f"{self.file_original_name}"


class LocationsAppSettings(models.Model):
    """
    This class is used to store the settings for the locations app.
    It will be a singleton model. This means that there will only be one instance of this model.
    """

    class Meta:
        """
        Override the verbose name for this model.
        """

        verbose_name_plural = "Map Settings"

    # Geodesic data
    # NB. min and maxes are set to different non 0 data to ensure no division
    # by 0 errors
    min_lat: models.FloatField = models.FloatField(default=0.2)
    min_lon: models.FloatField = models.FloatField(default=0.2)

    max_lat: models.FloatField = models.FloatField(default=0.1)
    max_lon: models.FloatField = models.FloatField(default=0.1)

    # World space data
    min_world_x: models.FloatField = models.FloatField(default=0.2)
    min_world_y: models.FloatField = models.FloatField(default=0.2)
    min_world_z: models.FloatField = models.FloatField(default=0.2)

    max_world_x: models.FloatField = models.FloatField(default=0.1)
    max_world_y: models.FloatField = models.FloatField(default=0.1)
    max_world_z: models.FloatField = models.FloatField(default=0.1)

    camera_z_map: models.ImageField = models.ImageField(
        upload_to="locations/camera_z_map/", blank=True, null=True
    )

    world_colour: models.CharField = models.CharField(
        max_length=7, default="#000000"
    )  # Hex colour code
    render_dist: models.IntegerField = models.IntegerField(default=250)

    # what goes before the slug of the qr code ie
    # 127.0.0.1:8000/locations/reached/
    qr_prefix: models.CharField = models.CharField(
        max_length=200, default="", blank=True, null=False
    )
    default_lat: models.FloatField = models.FloatField(
        default=0, blank=False, null=False
    )
    default_lon: models.FloatField = models.FloatField(
        default=0, blank=False, null=False
    )

    def save(self, *args, **kwargs) -> None:
        """
        Overriding the save method to ensure there is only one instance of this model.

        @param args: Likely None
        @param kwargs: Likely None
        @return: None
        """
        self.pk = 1  # Ensure there's only one instance
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """
        Prevent deletion of this model.

        @param args: Likely None.
        @param kwargs: Likely None.
        @return: None
        """
        return None  # Prevent deletion

    @classmethod
    def get_instance(cls) -> Self:
        """
        Static method to return the instance of this model.
        If there is no instance, it will create one.

        @return: The singleton instance of this model.
        """
        return cls.objects.first() or cls.objects.create()

    def __str__(self):
        """
        A nicer string representation of the model.

        @return: String representation of the model.
        """
        return "Site Settings"


class FeatureInstanceTileMap(models.Model):
    """
    This model links a FeatureInstance to a Map3DChunk.
    """

    feature_instance = models.ForeignKey(
        FeatureInstance, on_delete=models.CASCADE)
    map_chunk = models.ForeignKey(Map3DChunk, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns a string representation of the object.

        @return: The name of the feature and the original file name of the map chunk.
        """
        return (f'{self.feature_instance.feature.name} "{self.feature_instance.slug}" in "'
                f'{self.map_chunk.file_original_name}"')


class QuestionFeature(models.Model):
    """
    If a FeatureInstance comes with a question then the question and answer are stored in this model
    The FeatureInstance model has an optional ForeignKey to this model
    """

    id: models.AutoField = models.AutoField(primary_key=True)
    question_text: models.TextField = models.TextField(blank=False, null=False)
    feature: models.ForeignKey = models.ForeignKey(
        FeatureInstance, on_delete=models.CASCADE
    )

    case_sensitive: models.BooleanField = models.BooleanField(default=False)
    use_fuzzy_comparison: models.BooleanField = models.BooleanField(
        default=False)
    fuzzy_threshold: models.IntegerField = models.IntegerField(
        default=65, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        """
        Returns a string representation of the object.
        @return: The question.
        """
        return f"{self.question_text}"

    def is_valid_answer(self, input_answer: str) -> bool:
        """
        This function checks if a given answer is valid for this question

        @param input_answer: The answer to query
        @return: A bool true or false for if this is a valid answer
        """

        # get all the answers for this question
        answers: list[str] = [
            answer.choice_text for answer in self.questionanswer_set.all()
        ]

        valid = False
        for correct_answer in answers:
            correct_answer = (correct_answer.lower()
                              if not self.case_sensitive else correct_answer)
            input_answer = (
                input_answer.lower() if not self.case_sensitive else input_answer)

            valid_non_fuzzy = (
                not self.use_fuzzy_comparison and input_answer == correct_answer)
            valid_fuzzy = (self.use_fuzzy_comparison and fuzz.ratio(
                input_answer, correct_answer) > self.fuzzy_threshold)

            if valid_fuzzy or valid_non_fuzzy:
                valid = True
                break

        return valid


class QuestionAnswer(models.Model):
    """
    This model stores the possible answers to a question
    """
    question = models.ForeignKey(QuestionFeature, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        """
        Returns a string representation of the object.

        @return: The choice text.
        """
        return self.choice_text
