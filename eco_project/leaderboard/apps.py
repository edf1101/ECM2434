"""
This file is used to configure the leaderboard app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    """
    Configuration class for the leaderboard app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "leaderboard"
