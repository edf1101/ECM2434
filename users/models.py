"""
This module contains the models needed for the users app
"""
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum




class Profile(models.Model):
    """
    This model extends the User model to include additional data.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0, blank=False, null=False)
    bio = models.TextField(blank=True, null=False)
    longitude = models.FloatField(blank=False, null=False, default=0)
    latitude = models.FloatField(blank=False, null=False, default=0)

    def update_points(self):
        """
        Updates the points field with the sum of all owned pets' points
        """
        total_points = self.user.pets.aggregate(Sum('points'))['points__sum'] or 0
        self.points = total_points
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Badge(models.Model):
    """
    This model represents a badge that a user can earn.
    """

    title: models.CharField = models.CharField(primary_key=True, null=False, blank=False,
                                               max_length=50)
    hover_text: models.CharField = models.CharField(max_length=100)
    colour: models.CharField = models.CharField(max_length=7, null=False, blank=False,
                                                default="#FF0000")
    rarity: models.IntegerField = models.IntegerField(null=False, blank=False, default=1,
                                                      validators=[MinValueValidator(0),
                                                                  MaxValueValidator(10)], )

    def __str__(self):
        return self.title


class BadgeInstance(models.Model):
    """
    This model represents an instance of a badge that a user has earned.
    """

    badge: models.ForeignKey = models.ForeignKey(Badge, on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.badge.title}"

    class Meta:
        """
        This ensures that a user can only have one instance of a badge.
        """
        unique_together = ('user', 'badge')
