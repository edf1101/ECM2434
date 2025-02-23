"""
This file contains the URL patterns for the leaderboard app.
"""
from django.urls import path

from .views import leaderboard_view

app_name = "leaderboard"

urlpatterns = [
    path("", leaderboard_view, name="leaderboard"),
]
