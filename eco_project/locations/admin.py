"""
This class deals with how the models appear in the admin menu.
"""
from django.contrib import admin
from .models import Feature, IndividualFeature
from .forms import FeatureForm


class FeatureAdmin(admin.ModelAdmin):
    """
    This class decides how the Feature model appears in the admin menu.
    It has two sections, Feature Info and Display information.
    """
    form = FeatureForm
    fieldsets = [
        ("Feature Info", {"fields": ["name", "description"]}),
        ("Display information", {"fields": ["colour", "generic_img"]}),
    ]
    search_fields = ["name"]
    list_display = ["name", "description"]


class IndividualFeatureAdmin(admin.ModelAdmin):
    """
    This class decides how the IndividualFeature model appears in the admin menu.
    It has three sections, Feature Info, Location and Display information.
    """
    fieldsets = [
        ("Feature Info", {"fields": ["name", "feature", "slug"]}),
        ("Location", {"fields": ["longitude", "latitude"]}),
        ("Display information", {"fields": ["specific_img"]}),
    ]
    list_display = ["slug", "feature", "longitude", "latitude"]
    search_fields = ["feature"]


# Register the models with their respective classes.
admin.site.register(Feature, FeatureAdmin)
admin.site.register(IndividualFeature, IndividualFeatureAdmin)
