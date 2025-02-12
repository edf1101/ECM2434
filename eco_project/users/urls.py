"""
This file contains the URL patterns for the users app.
"""
from django.urls import path
from . import views
from . import api

app_name = 'users'

urlpatterns = [
    path('registration/', views.registration_view, name="registration"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
]
