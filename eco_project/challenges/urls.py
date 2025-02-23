"""
This file contains the URL patterns for the challenges app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.urls import path

# from . import views
from . import api

app_name = "challenges"

urlpatterns = [
    path("update_streak/", api.collect_streak, name="update_streak"),
    path("submit_answer/", api.submit_answer_api, name="submit_answer_api"),
    path("get_nearby_challenges/", api.nearest_challenges_api, name="get_nearby_challenges", ),
]
