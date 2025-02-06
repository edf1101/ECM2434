"""
This file contains the models for the locations app.
The models are used to store information about the different types of sustainability features
and their locations.
"""
from django.db import models


# Create your models here.

class Feature(models.Model):
    """
    A model to store a sustainability feature. Ie Recycling bin, water fountain, etc.
    """
    id: models.AutoField = models.AutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField()
    colour = models.CharField(max_length=7, default="#000000")  # Hex colour code

    def __str__(self):
        return f'{self.name}'


class IndividualFeature(models.Model):
    """
    A model to store a feature that is specific to a location. Ie a recycling bin outside the forum.
    """
    id: models.AutoField = models.AutoField(primary_key=True)
    feature: models.ForeignKey = models.ForeignKey(Feature, on_delete=models.CASCADE)
    longitude: models.FloatField = models.FloatField()
    latitude: models.FloatField = models.FloatField()
    # models.

    def __str__(self):
        return f'{self.feature.name} at lon:{self.longitude:.3f}, lat:{self.latitude:.3f}'
