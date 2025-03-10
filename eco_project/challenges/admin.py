"""
Admin panel configuration for Streak and StreakSettings models.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.contrib import admin
import nested_admin
from .models import Streak, ChallengeSettings, UserFeatureReach, Choice, Question, Quiz, QuizAttempt

#pylint: disable=E1101

class StreakAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Streak model.
    """

    list_display = (
        "user",
        "raw_count",
        "last_window",
        "effective_streak",
        "running_out",
    )
    readonly_fields = ("effective_streak", "running_out")


class ChallengeSettingsAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Challenge settings model.
    """

    fieldsets = (
        ("Streak Settings", {"fields": ("interval",)}),
        (
            "Points Settings",
            {"fields": ("question_feature_points", "reached_feature_points")},
        ),
    )


class ChoiceInline(nested_admin.NestedTabularInline):
    """
    This is the admin panel configuration for the Choice model
    """
    model = Choice
    extra = 2

class QuestionInline(nested_admin.NestedStackedInline):
    """
    This is the admin panel configuration for the Question model.
    It has the choices inline.
    """
    model = Question
    extra = 1
    inlines = [ChoiceInline]

@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    """
    This is the admin panel configuration for the Quiz model.
    It uses nested inline to have the quiz, questions and choices all in one admin form.
    """
    inlines = [QuestionInline]


admin.site.register(UserFeatureReach)
admin.site.register(Streak, StreakAdmin)
admin.site.register(ChallengeSettings, ChallengeSettingsAdmin)
admin.site.register(QuizAttempt)
