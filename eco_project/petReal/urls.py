from django.urls import path

from . import views

# from . import api

app_name = "petreal"

urlpatterns = [
    path("", views.petreal_home, name="home"),
]
