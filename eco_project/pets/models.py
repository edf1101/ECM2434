from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.

class PetType(models.Model):
    """
    A model to store a type of pet
    """
    id: models.AutoField = models.AutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=200, unique=True)
    description: models.TextField = models.TextField()

    base_image: models.ImageField = models.ImageField(
        upload_to='pets/pet_imgs/',
        blank=False)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of the pet type.
        """
        return f'{self.name}'

class Pet(models.Model):
    """
    A model to store a specific user's pet
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey(PetType, on_delete=models.PROTECT) # Do not allow a PetType to be deleted if pets still exist of that type

    points = models.IntegerField(default=0)
    health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # TODO
    # owner: models.ForeignKey(...)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of this pet and its type.
        """
        return f'{self.name} ({self.type.name})'