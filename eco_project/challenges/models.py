"""
Models for the Challenges app.
"""
from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from .streaks import get_current_window  # make sure this helper works as expected


class ChallengeSettings(models.Model):
    """
    Singleton model to store the Challenge app settings
    """

    interval = models.DurationField(default=timedelta(days=1))  # adjustable interval

    def __str__(self):
        return f"Interval: {self.interval}"

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure only one instance of this model exists.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Returns the single StreakSettings instance, creating it if there isnt one already.
        """

        obj, created = cls.objects.get_or_create(pk=1, defaults={'interval': timedelta(days=1)})
        return obj

    class Meta:
        """
        Override the verbose name for this model.
        """
        verbose_name_plural = "Challenge Settings"


class Streak(models.Model):
    """
    Model to store the streak count for each user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    raw_count = models.IntegerField(default=0)
    # Stores the start of the window when the user last checked in.
    last_window = models.DateTimeField(null=True, blank=True)

    @property
    def effective_streak(self) -> int:
        """
        Returns the user's effective streak count.
        If the last check-in window is not the current or immediately previous one,
        the streak is considered broken.

        @returns int: The effective streak count.
        """
        settings_obj = ChallengeSettings.get_solo()
        interval = settings_obj.interval
        now_time = timezone.now()
        current_window_start, _ = get_current_window(now_time, interval)
        previous_window_start = current_window_start - interval

        if self.last_window in [previous_window_start, current_window_start]:
            return self.raw_count
        return 0

    @property
    def running_out(self) -> bool:
        """
        Returns True if the user's streak is about to be broken.
        """
        if self.effective_streak == 0:  # no streak to run out of
            return False

        settings_obj = ChallengeSettings.get_solo()
        interval = settings_obj.interval
        now_time = timezone.now()
        current_window_start, _ = get_current_window(now_time, interval)
        return self.last_window != current_window_start

    def __str__(self):
        return f"{self.user.username} - Streak: {self.effective_streak}"
