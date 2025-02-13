"""
This file is automatically created when you create a new app in Django.
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

        :return: None
        """
        import locations.signals
