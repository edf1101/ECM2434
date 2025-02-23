"""
This file is used to configure the app name for the users app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    This class is used to configure the app name for the users app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """
        This method is called when the app is ready to be used.
        """
        # pylint: disable=unused-import, import-outside-toplevel
        import users.signals  # to create user profiles when new users are created
