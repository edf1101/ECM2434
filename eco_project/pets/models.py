"""
This module contains the models for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import PROTECT
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

    base_video = models.FileField(upload_to="pets/videos/", blank=False)

    def __str__(self) -> str:
        """
        Returns the name of the pet type.

        @return: The name of the pet type.
        """
        return self.name


class CosmeticCategory(models.Model):
    """
    A model to store a type of cosmetic (i.e. Hat, Scarf)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        """
        Returns the name of the cosmetic category.

        @return: The name of the cosmetic category.
        """
        return self.name


class Cosmetic(models.Model):
    """
    A model to store a specific cosmetic (i.e. Red Scarf)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.ForeignKey(CosmeticCategory, on_delete=models.PROTECT)
    fits = models.ForeignKey(PetType, on_delete=models.CASCADE, blank=True, null=True)
    icon = models.FileField(upload_to="pets/cosmetic_icons/", blank=False)
    video = models.FileField(upload_to="pets/videos/", blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "fits"], name="unique_name_fits")
        ]

    def __str__(self) -> str:
        """
        Returns the name of the cosmetic.

        @return: The name of the cosmetic.
        """
        return f"{self.name} ({self.fits.name} {self.category.name})"


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
    low_health_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    current_cosmetic = models.ForeignKey(Cosmetic, blank=True, on_delete=PROTECT, null=True)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pet"
    )

    def __str__(self) -> str:
        """
        Returns the name of the pet.

        @return: The name of the pet
        """
        return f"{self.owner.username}'s {self.name} ({self.type.name})"
