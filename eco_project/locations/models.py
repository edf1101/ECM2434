"""
This file contains the models for the locations app.
The models are used to store information about the different types of sustainability features
and their locations.
"""
from django.db import models
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from typing import Self


# Create your models here.

class FeatureType(models.Model):
    """
    A model to store a sustainability feature. Ie Recycling bin, water fountain, etc.
    """
    id: models.AutoField = models.AutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField()
    colour = models.CharField(max_length=7, default="#000000")  # Hex colour code
    generic_img: models.ImageField = models.ImageField(
        upload_to='locations/feature_type_img/',
        blank=False)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of the feature.
        """
        return f'{self.name}'


class FeatureInstance(models.Model):
    """
    A model to store a feature type that is specific to a location. Ie a recycling bin outside the forum.
    """
    slug = models.SlugField(primary_key=True, max_length=200, unique=True, blank=False)
    name = models.CharField(max_length=200, blank=False)
    feature = models.ForeignKey(FeatureType, on_delete=models.CASCADE)
    longitude = models.FloatField()
    latitude = models.FloatField()
    specific_img = models.ImageField(upload_to='locations/feature_instance_img/', blank=True,
                                     null=True)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: the name of the feature and the slug.
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
    file: models.FileField = models.FileField(upload_to='locations/3d_map_chunks/', blank=False)
    file_original_name: models.CharField = models.CharField(max_length=200, blank=False)

    # geodesic data
    center_lat: models.FloatField = models.FloatField(blank=False, default=0)
    center_lon: models.FloatField() = models.FloatField(blank=False, default=0)

    bottom_left_lat: models.FloatField = models.FloatField(blank=False, default=0)
    bottom_left_lon: models.FloatField() = models.FloatField(blank=False, default=0)

    top_right_lat: models.FloatField = models.FloatField(blank=False, default=0)
    top_right_lon: models.FloatField() = models.FloatField(blank=False, default=0)

    # blender data
    bottom_left_x: models.FloatField = models.FloatField(blank=False, default=0)
    bottom_left_y: models.FloatField() = models.FloatField(blank=False, default=0)
    bottom_left_z: models.FloatField() = models.FloatField(blank=False, default=0)

    top_right_x: models.FloatField = models.FloatField(blank=False, default=0)
    top_right_y: models.FloatField() = models.FloatField(blank=False, default=0)
    top_right_z: models.FloatField() = models.FloatField(blank=False, default=0)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The original file name.
        """
        return f'{self.file_original_name}'


class LocationsAppSettings(models.Model):
    """
    This class is used to store the settings for the locations app.
    It will be a singleton model. This means that there will only be one instance of this model.
    """

    # Geodesic data
    # NB. min and maxes are set to different non 0 data to ensure no division by 0 errors
    min_lat = models.FloatField(default=0.2)
    min_lon = models.FloatField(default=0.2)

    max_lat = models.FloatField(default=0.1)
    max_lon = models.FloatField(default=0.1)

    # World space data
    min_world_x = models.FloatField(default=0.2)
    min_world_y = models.FloatField(default=0.2)
    min_world_z = models.FloatField(default=0.2)

    max_world_x = models.FloatField(default=0.1)
    max_world_y = models.FloatField(default=0.1)
    max_world_z = models.FloatField(default=0.1)

    def save(self, *args, **kwargs) -> None:
        """
        Overriding the save method to ensure there is only one instance of this model.

        :param args: Likely None
        :param kwargs: Likely None
        :return: None
        """
        self.pk = 1  # Ensure there's only one instance
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """
        Prevent deletion of this model.

        :param args: Likely None.
        :param kwargs: Likely None.
        :return: None
        """
        pass  # Prevent deletion

    @classmethod
    def get_instance(cls) -> Self:
        """
        Static method to return the instance of this model.
        If there is no instance, it will create one.

        :return: The singleton instance of this model.
        """
        return cls.objects.first() or cls.objects.create()

    def __str__(self):
        """
        A nicer string representation of the model.

        :return: String representation of the model.
        """
        return "Site Settings"
