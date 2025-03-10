from django.urls import path
from . import views

urlpatterns = [
    path("spin/", views.spin_lootbox, name="spin_lootbox"),
]
