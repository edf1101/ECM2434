from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ReactionType(models.Model):
    """
    This class represents the reaction type model.
    This is a reaction to a petReal post.
    """
    name = models.CharField(max_length=50, blank=False, null=False)
    icon = models.CharField(max_length=3, blank=False, null=False, primary_key=True, unique=True)

    def __str__(self) -> str:
        """
        This method returns the name of the reaction type.
        """
        return f'{self.name} ({self.icon})'


class UserPhoto(models.Model):
    """
    This class represents the photo that a user takes as their PetReal.
    """
    photo = models.ImageField(upload_to='petReal/photos/', blank=True, null=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='UserPhoto',
                                   primary_key=True, blank=False, null=False, unique=True)
    expiration_date = models.DateTimeField(blank=False, null=False)

    def __str__(self) -> str:
        """
        This method returns the str description of the user photo.
        """
        return f"{self.user_id}'s photo"


class UserPhotoReaction(models.Model):
    """
    This class represents the reaction to a user photo.
    """
    reactor = models.ForeignKey(User, on_delete=models.CASCADE)
    reacted_photo = models.ForeignKey(UserPhoto, on_delete=models.CASCADE)
    reaction_type_id = models.ForeignKey('ReactionType', on_delete=models.CASCADE, blank=False,
                                         null=False)

    def __str__(self) -> str:
        """
        This method returns the str description of the user photo reaction.
        """
        return (f"{self.reactor} "
                f"reacted {self.reaction_type_id.icon} "
                f"to {self.reacted_photo.user_id}'s photo")
