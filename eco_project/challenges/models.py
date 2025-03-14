"""
Models for the Challenges app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from locations.models import FeatureInstance

from .challenge_helpers import get_current_window  # make sure this helper works as expected

User = get_user_model()


class ChallengeSettings(models.Model):
    """
    Singleton model to store the Challenge app settings
    """

    interval = models.DurationField(
        default=timedelta(
            days=1))  # The interval in which the user must check in to maintain their streak
    question_feature_points: models.IntegerField = models.IntegerField(
        default=2
    )  # points per correct answer
    reached_feature_points: models.IntegerField = models.IntegerField(
        default=1
    )  # points per reached normal feature

    def __str__(self):
        """
        Override the string representation of this model.
        """
        return "Challenge Settings"

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure only one instance of this model exists.

        @param args: Additional arguments.
        @param kwargs: Additional keyword
        @return: None
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Returns the single StreakSettings instance, creating it if there isnt one already.

        @return: The single StreakSettings instance.
        """

        obj, _ = cls.objects.get_or_create(
            pk=1, defaults={"interval": timedelta(days=1)}
        )
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

        @return int: The effective streak count.
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

        @return: True if the streak is about to be broken, False otherwise.
        """
        if self.effective_streak == 0:  # no streak to run out of
            return False

        settings_obj = ChallengeSettings.get_solo()
        interval = settings_obj.interval
        now_time = timezone.now()
        current_window_start, _ = get_current_window(now_time, interval)
        return self.last_window != current_window_start

    def __str__(self):
        """
        Override the string representation of this model.

        @return: The string representation of this model.
        """
        return f"{self.user.username} - Streak: {self.effective_streak}"


class UserFeatureReach(models.Model):
    """
    This model holds the unique relationship of features that a user has reached.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feature_instance = models.ForeignKey(
        FeatureInstance, on_delete=models.CASCADE)
    reached_at = models.DateTimeField(auto_now_add=True)
    extra = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        """
        Override the string representation of this model.

        @return: The string representation of this model.
        """
        return (
            f"{self.user.username} reached {self.feature_instance} at {self.reached_at}"
        )


class Quiz(models.Model):
    """
    This model holds the quizzes that a user can complete.
    """
    title = models.CharField(max_length=200)
    total_points = models.PositiveIntegerField(default=10)

    def __str__(self) -> str:
        """
        The string representation of this model.
        """
        return self.title


class Question(models.Model):
    """
    This model holds the questions for each quiz.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self) -> str:
        """
        The string representation of this model.
        """
        return self.text


class Choice(models.Model):
    """
    This model holds the choices for each question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        """
        The string representation of this model.
        """
        return self.text

class QuizAttempt(models.Model):
    """
    This model holds the attempts of users on quizzes.
    It is used so the site can determine if a user has already attempted a quiz.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    answers = models.CharField(max_length=255) # This holds a users past answers ie ABB
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        The string representation of this model.
        """
        return f"{self.user} - {self.quiz} ({self.score})"
