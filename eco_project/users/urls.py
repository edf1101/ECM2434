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
    path('edit/', views.edit_profile, name="edit"),
    path('change_password/', views.change_password, name='password_change'),
    path("profile/<str:username>/", views.profile_view, name="user_profile"),
    path('api/update_location/', api.update_location, name='update_location'),
]
