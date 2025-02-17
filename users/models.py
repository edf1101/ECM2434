"""
This module contains the models needed for the users app
"""
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from random import choices


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


def generate_unique_code():
    length = 6
    while True:
        # Generate a random 6-letter uppercase string
        code = ''.join(choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))
        # Check for uniqueness in the database
        if not UserGroup.objects.filter(code=code).exists():
            return code

class UserGroup(models.Model):
    """
    This model represents a group of users.
    """
    code = models.CharField(
        max_length=6,  # exactly 6 characters
        unique=True,
        primary_key=True,
        default=generate_unique_code
    )
    users = models.ManyToManyField(User, blank=True)
    group_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administered_groups',
        help_text="The admin for the group. Must be a member of the group."
    )

    @property
    def users_in_group(self) -> str:
        """
        Returns a string listing the users in the group
        :return: a string listing the users in the group
        """
        return ', '.join(user.username for user in self.users.all())

    def add_user(self, user: User) -> None:
        """
        Add a user to the group.
        """
        self.users.add(user)

    def remove_user(self, user: User) -> None:
        """
        Remove a user from the group.
        Cannot remove the group admin

        :param user: the user to remove
        """
        if self.group_admin == user:
            raise ValueError("Cannot remove the group admin")
        self.users.remove(user)

    def __str__(self) -> str:
        """
        Return a string representation of the group

        :return: a string representation of the group
        """
        return f"Group {self.code}"
