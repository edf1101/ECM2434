"""
This file is used to define the URL patterns for the lootboxes app.
"""

from django.urls import path
from . import views

app_name = 'lootboxes'
urlpatterns = [
    path('', views.wheel_view, name='spin'),
    path('api/spin/', views.spin_wheel, name='spin_wheel'),
]
