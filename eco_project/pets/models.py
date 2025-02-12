from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class PetType(models.Model):
    """
    A model to store a type of pet (i.e. Dog, Cat)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()

    base_image = models.ImageField(
        upload_to='pet_imgs/',
        name="Base Image",
        blank=False)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of the pet type.
        """
        return f'{self.name}'


class CosmeticType(models.Model):
    """
    A model store a type of cosmetic (i.e. Hat, Scarf)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    x = models.FloatField(name="X Position")
    y = models.FloatField(name="Y Position")

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of this cosmetic typw.
        """
        return f'{self.name}'


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
        """
        Returns a string representation of the object.

        :return: The name of this cosmetic typw.
        """
        return f'{self.name} ({self.type.name})'

class Pet(models.Model):
    """
    A model to store a specific user's pet
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey(PetType, on_delete=models.PROTECT) # Do not allow a PetType to be deleted if pets still exist of that type

    points = models.IntegerField(default=0)
    health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cosmetics = models.ManyToManyField(Cosmetic, blank=True)

    # TODO Point to user model once it has been created
    # owner = models.OneToOneField("User", on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: The name of this pet and its type.
        """
        return f'{self.name} ({self.type.name})'
