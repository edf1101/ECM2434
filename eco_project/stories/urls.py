"""
This file is used to define the URL patterns for the stories app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.urls import path

from . import views

from . import api

app_name = "stories"

urlpatterns = [
    path("", views.stories_home, name="home"),
    path("api/add-reaction", api.add_reaction, name="add_reaction"),
    path("api/add-photo", api.add_story, name="add_photo"),
]
