"""
This file contains the models for the locations app.
The models are used to store information about the different types of sustainability features
and their locations.
"""
from django.db import models
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile


# Create your models here.

class Feature(models.Model):
    """
    A model to store a sustainability feature. Ie Recycling bin, water fountain, etc.
    """
    id: models.AutoField = models.AutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField()
    colour = models.CharField(max_length=7, default="#000000")  # Hex colour code
    generic_img: models.ImageField = models.ImageField(upload_to='generic_feature_images/',
                                                       blank=False)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of the feature.
        """
        return f'{self.name}'


class IndividualFeature(models.Model):
    """
    A model to store a feature that is specific to a location. Ie a recycling bin outside the forum.
    """
    slug = models.SlugField(primary_key=True, max_length=200, unique=True, blank=False)
    name = models.CharField(max_length=200, blank=False)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    longitude = models.FloatField()
    latitude = models.FloatField()
    specific_img = models.ImageField(upload_to='specific_feature_images/', blank=True, null=True)

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
