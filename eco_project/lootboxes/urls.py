from django.urls import path
from . import views

app_name = "lootboxes"

urlpatterns = [
    path("spin/", views.spin_lootbox, name="spin_lootbox"),
]
