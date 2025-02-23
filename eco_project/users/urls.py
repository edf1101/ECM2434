"""
This file contains the URL patterns for the users app.
"""
from django.urls import path

from . import api
from . import views

app_name = "users"

urlpatterns = [
    path("registration/", views.registration_view, name="registration"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("edit/", views.edit_profile, name="edit"),
    path("change_password/", views.change_password, name="password_change"),
    path("profile/<str:username>/", views.profile_view, name="user_profile"),
    path("api/update_location/", api.update_location, name="update_location"),
    path("groups/", views.groups_home, name="group_home"),
    path("api/groups/create/", api.create_group, name="create_group"),
    path("api/groups/<str:code>/delete/", api.delete_group, name="delete_group"),
    path(
        "api/groups/<str:code>/remove_user/",
        api.remove_user_from_group,
        name="remove_user",
    ),
    path("api/groups/join/", api.join_group, name="join_group"),
    path("api/groups/<str:code>/leave/", api.leave_group, name="leave_group"),
]
