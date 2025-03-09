"""
This file contains the URL patterns for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.urls import path

from . import api
from . import views

app_name = "pets"

urlpatterns = [
    path(
        "mypet/",
        views.view_pet,
        name="mypet"),
    path(
        "accessories/", 
        views.accessories, 
        name="accessories"),
    path(
        "api/get_pet_data/<str:username>/",
        api.get_pet_data,
        name="get_pet_data"),
]
