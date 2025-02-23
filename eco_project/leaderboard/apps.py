"""
This file is used to configure the leaderboard app.
"""
from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    """
    Configuration class for the leaderboard app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "leaderboard"
