"""
This file contains the URL patterns for the challenges app.
"""
from django.urls import path

# from . import views
from . import api

app_name = 'challenges'

urlpatterns = [
    path('update_streak/', api.collect_streak, name="update_streak"),

]
