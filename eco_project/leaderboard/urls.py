"""
This file contains the URL patterns for the leaderboard app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.urls import path

from .views import leaderboard_view

app_name = "leaderboard"

urlpatterns = [
    path("", leaderboard_view, name="leaderboard"),
]
