"""
This file is automatically created when you create a new app in Django.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.apps import AppConfig


class LocationsConfig(AppConfig):
    """
    Configuration for the locations app
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "locations"

    def ready(self) -> None:
        """
        When the app is set up it imports the signals from the signals file

        @return: None
        """
        # pylint: disable=unused-import, import-outside-toplevel
        import locations.signals
