from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class PetType(models.Model):
    """
    A model to store a type of pet (i.e. Dog, Cat)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)  # Single definition
    description = models.TextField()
    base_image = models.ImageField(upload_to='pets/base_imgs/', blank=False)

    def __str__(self):
        return self.name

class CosmeticType(models.Model):
    """
    A model to store a type of cosmetic (i.e. Hat, Scarf)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    x = models.FloatField()
    y = models.FloatField()

    def __str__(self):
        return self.name

class Cosmetic(models.Model):
    """
    A model to store a specific cosmetic (i.e. Red Scarf)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    type = models.ForeignKey(CosmeticType, on_delete=models.PROTECT)
    fits = models.ManyToManyField(PetType, blank=False)

    def __str__(self):
        return f'{self.name} ({self.type.name})'

class Pet(models.Model):
    """
    A model to store a specific user's pet
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey(PetType, on_delete=models.PROTECT)  # Reference to global PetType

    health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cosmetics = models.ManyToManyField(Cosmetic, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')

    def save(self, *args, **kwargs):
        """
        Override save method to update the user's points whenever a pet's points are updated.
        """
        # Save the pet first
        super().save(*args, **kwargs)

        # After saving, update the user's profile points
        if self.owner.profile:
            self.owner.profile.update_points()  # This will update the user's points based on their pets

    def __str__(self):
        return f"{self.owner.username}'s {self.name} ({self.type.name})"
