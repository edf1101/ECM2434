from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

class PetType(models.Model):
    """
    A model to store a type of pet
    """
    id: models.AutoField = models.AutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=200, unique=True)
    description: models.TextField = models.TextField()

    base_image: models.ImageField = models.ImageField(
        upload_to='pet_imgs/',
        blank=False)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of the pet type.
        """
        return f'{self.name}'

class Pet(models.Model):
    """
    A model to store a specific user's pet.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey('PetType', on_delete=models.PROTECT)
    points = models.IntegerField(default=0)
    health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')

    def __str__(self):
        return f'{self.name} ({self.type.name})'