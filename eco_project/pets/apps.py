"""
This file is used to configure the application and its signals.
"""
from django.apps import AppConfig

# these are needed to import the signals the pylint error is a mistake
# pylint: disable=unused-import, import-outside-toplevel

class PetsConfig(AppConfig):
    """
    Configuration for the pets app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pets"

    def ready(self):
        import pets.signals
