"""
This module contains the models needed for the users app
"""
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    This model extends the User model to include additional data.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    points = models.IntegerField(default=0, blank=False, null=False)
    bio = models.TextField(blank=True, null=False)

    longitude = models.FloatField(blank=False, null=False, default=0)
    latitude = models.FloatField(blank=False, null=False, default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"
