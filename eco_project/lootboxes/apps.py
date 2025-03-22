"""
This file is used to configure the app name for the Django admin panel.
"""

from django.apps import AppConfig


class LootboxesConfig(AppConfig):
    """
    Configuration class for the lootboxes app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "lootboxes"
