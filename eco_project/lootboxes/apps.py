"""
This file is used to configure the app name for the Django admin panel.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.apps import AppConfig


class LootboxesConfig(AppConfig):
    """
    Configuration class for the lootboxes app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "lootboxes"
