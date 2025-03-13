"""
This file is used to configure the application and its signals.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
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
