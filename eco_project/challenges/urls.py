"""
This file contains the URL patterns for the challenges app.
"""
from django.urls import path
# from . import views
from . import api

app_name = 'challenges'

urlpatterns = [
    path('update_streak/', api.collect_streak, name="update_streak"),
    path('submit_answer/', api.submit_answer_api, name='submit_answer_api'),
    path('get_nearby_challenges/', api.nearest_challenges_api, name='get_nearby_challenges'),
]
