"""
This module contains the models for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class PetType(models.Model):
    """
    A model to store a type of pet (i.e. Dog, Cat)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)  # Single definition
    description = models.TextField()

    base_image = models.ImageField(upload_to="pets/base_imgs/", blank=False)
    video = models.FileField(upload_to="pets/videos/", blank=False)

    def __str__(self) -> str:
        """
        Returns the name of the pet type.

        @return: The name of the pet type.
        """
        return self.name


class CosmeticType(models.Model):
    """
    A model to store a type of cosmetic (i.e. Hat, Scarf)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    x = models.FloatField()
    y = models.FloatField()

    def __str__(self) -> str:
        """
        Returns the name of the cosmetic type.

        @return: The name of the cosmetic type.
        """
        return self.name


class Cosmetic(models.Model):
    """
    A model to store a specific cosmetic (i.e. Red Scarf)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    type = models.ForeignKey(CosmeticType, on_delete=models.PROTECT)
    fits = models.ManyToManyField(PetType, blank=False)
    image = models.ImageField(upload_to="pets/cosmetic_imgs/", blank=False)

    def __str__(self) -> str:
        """
        Returns the name of the cosmetic.

        @return: The name of the cosmetic.
        """
        return f"{self.name} ({self.type.name})"


class Pet(models.Model):
    """
    A model to store a specific user's pet
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey(
        PetType, on_delete=models.PROTECT
    )  # Reference to global PetType

    health = models.IntegerField(default=100,
                                 validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(default=timezone.now)
    cosmetics = models.ManyToManyField(Cosmetic, blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets")

    def __str__(self) -> str:
        """
        Returns the name of the pet.

        @return: The name of the pet
        """
        return f"{self.owner.username}'s {self.name} ({self.type.name})"
