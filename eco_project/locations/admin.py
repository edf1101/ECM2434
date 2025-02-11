"""
This class deals with how the models appear in the admin menu.
"""
from django.contrib import admin
from .models import FeatureType, FeatureInstance, Map3DChunk, LocationsAppSettings, \
    FeatureInstanceTileMap
from .forms import FeatureForm, LocationsAppSettingsForm


class FeatureTypeAdmin(admin.ModelAdmin):
    """
    This class decides how the FeatureType model appears in the admin menu.
    It has two sections, Feature Info and Display information.
    """
    form = FeatureForm
    fieldsets = [
        ("Feature Info", {"fields": ["name", "description"]}),
        ("Display information", {"fields": ["colour", "generic_img", "feature_mesh"]}),
    ]
    search_fields = ["name"]
    list_display = ["name", "description"]


class FeatureInstanceAdmin(admin.ModelAdmin):
    """
    This class decides how the FeatureInstance model appears in the admin menu.
    It has three sections, Feature Info, Location and Display information.
    """
    fieldsets = [
        ("Feature Info", {"fields": ["name", "feature", "slug"]}),
        ("Location", {"fields": ["longitude", "latitude"]}),
        ("Display information", {"fields": ["specific_img"]}),
    ]
    list_display = ["slug", "feature", "longitude", "latitude"]
    search_fields = ["feature"]


class Map3DChunkAdmin(admin.ModelAdmin):
    """
    This class decides how the IndividualFeature model appears in the admin menu.
    It has three sections, Feature Info, Location and Display information.
    """
    fieldsets = [
        ("File", {"fields": ["file", "file_original_name"]}),
        ("Geodesic Coordinates", {"fields": ["center_lat", "center_lon",
                                             "bottom_left_lat", "bottom_left_lon",
                                             "top_right_lat", "top_right_lon"]}),
        ("World space Coordinates", {"fields": ["bottom_left_x", "bottom_left_y", "bottom_left_z",
                                                "top_right_x", "top_right_y", "top_right_z"]}),
    ]
    list_display = ["file_original_name"]
    search_fields = ["file_original_name"]


class LocationAppSettingsAdmin(admin.ModelAdmin):
    """
    This class decides how the LocationsAppSettings model appears in the admin menu.
    """

    # create a description for this admin page
    readonly_fields = ('desc',)  # Add the method name here

    def desc(self, obj=None) -> str:
        """
        Returns a description of the page.

        :param obj: None
        :return: A string description of the page.
        """
        return "This page is a singleton model that stores the settings for the Locations app."

    desc.short_description = "Description"
    form = LocationsAppSettingsForm

    fieldsets = [
        (None, {"fields": ["desc"]}),
        ("Geodesic Map Data", {"fields": ["min_lat", "max_lat", "min_lon", "max_lon"]},),
        ("World Space Data",
         {"fields": ["min_world_x", "max_world_x",
                     "min_world_y", "max_world_y",
                     "min_world_z", "max_world_z"]}),
        ("Camera Z Map", {"fields": ["camera_z_map"]}),
        ("Map Render Settings", {"fields": ["world_colour","render_dist"]}),
    ]


# Register the models with their respective classes.
admin.site.register(LocationsAppSettings, LocationAppSettingsAdmin)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(FeatureInstance, FeatureInstanceAdmin)
admin.site.register(Map3DChunk, Map3DChunkAdmin)

admin.site.register(FeatureInstanceTileMap)
