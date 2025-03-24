"""
This file is used to define the URL patterns for the lootboxes app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.urls import path
from . import views

app_name = 'lootboxes'
urlpatterns = [
    path('', views.wheel_view, name='spin'),
    path('api/spin/', views.spin_wheel, name='spin_wheel'),
]
