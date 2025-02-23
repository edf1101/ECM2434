"""
Admin panel configuration for Streak and StreakSettings models.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.contrib import admin

from .models import Streak, ChallengeSettings, UserFeatureReach


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


admin.site.register(UserFeatureReach)
admin.site.register(Streak, StreakAdmin)
admin.site.register(ChallengeSettings, ChallengeSettingsAdmin)
