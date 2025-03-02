"""
This class deals with how the models appear in the admin menu.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib import admin

from .forms import FeatureForm, LocationsAppSettingsForm
from .models import (
    FeatureType,
    FeatureInstance,
    LocationsAppSettings,
    QuestionFeature,
    QuestionAnswer,
    Map3DChunk,
    FeatureInstanceTileMap
)


class FeatureTypeAdmin(admin.ModelAdmin):
    """
    This class decides how the FeatureType model appears in the admin menu.
    It has two sections, Feature Info and Display information.
    """

    form = FeatureForm
    fieldsets = [
        ("Feature Info", {
            "fields": [
                "name", "description"]}), ("Display information", {
            "fields": [
                "colour", "generic_img", "feature_mesh"]}), ]
    search_fields = ["name"]
    list_display = ["name", "description"]


class FeatureInstanceAdmin(admin.ModelAdmin):
    """
    This class decides how the FeatureInstance model appears in the admin menu.
    It has three sections, Feature Info, Location and Display information.
    """

    readonly_fields = (
        "has_challenge",
        "has_question",
    )  # So you can see the challenge status

    fieldsets = [
        ("Feature Info", {"fields": ["name", "feature", "slug"]}),
        ("Location", {"fields": ["longitude", "latitude"]}),
        ("Display information", {"fields": ["specific_img","instance_description"]}),
        ("Challenge Info", {"fields": ["has_challenge", "has_question"]}),
        ("QR Code", {"fields": ["qr_code"]}),
    ]
    list_display = [
        "slug",
        "feature",
        "longitude",
        "latitude",
        "has_challenge"]
    search_fields = ["feature"]


class Map3DChunkAdmin(admin.ModelAdmin):
    """
    This class decides how the IndividualFeature model appears in the admin menu.
    It has three sections, Feature Info, Location and Display information.
    """

    fieldsets = [
        ("File", {"fields": ["file", "file_original_name"]}),
        (
            "Geodesic Coordinates",
            {
                "fields": [
                    "center_lat",
                    "center_lon",
                    "bottom_left_lat",
                    "bottom_left_lon",
                    "top_right_lat",
                    "top_right_lon",
                ]
            },
        ),
        (
            "World space Coordinates",
            {
                "fields": [
                    "bottom_left_x",
                    "bottom_left_y",
                    "bottom_left_z",
                    "top_right_x",
                    "top_right_y",
                    "top_right_z",
                ]
            },
        ),
    ]
    list_display = ["file_original_name"]
    search_fields = ["file_original_name"]


class LocationAppSettingsAdmin(admin.ModelAdmin):
    """
    This class decides how the LocationsAppSettings model appears in the admin menu.
    """

    # create a description for this admin page
    readonly_fields = ("desc",)  # Add the method name here

    # is needed to avoid pylint error which django forces
    # pylint: disable=W0613
    def desc(self, obj=None) -> str:
        """
        Returns a description of the page.

        @param obj: None
        @return: A string description of the page.
        """
        return "This page is a singleton model that stores the settings for the Locations app."

    desc.short_description = "Description"
    form = LocationsAppSettingsForm

    fieldsets = [
        (None, {"fields": ["desc"]}),
        (
            "Geodesic Map Data",
            {"fields": ["min_lat", "max_lat", "min_lon", "max_lon"]},
        ),
        (
            "World Space Data",
            {
                "fields": [
                    "min_world_x",
                    "max_world_x",
                    "min_world_y",
                    "max_world_y",
                    "min_world_z",
                    "max_world_z",
                ]
            },
        ),
        ("Camera Z Map", {"fields": ["camera_z_map"]}),
        ("Map Render Settings", {"fields": ["world_colour", "render_dist"]}),
        ("QR Code Settings", {"fields": ["qr_prefix"]}),
        ("Default Position", {"fields": ["default_lat", "default_lon"]}),
    ]


class QuestionAnswerInline(admin.TabularInline):
    """
    This inline model means you edit QuestionAnswers in the QuestionFeature page.
    """

    model = QuestionAnswer
    extra = 0


class QuestionFeatureAdmin(admin.ModelAdmin):
    """
    This admin page is for creating and editing QuestionFeatures.
    """

    fieldsets = [
        ("Question Details", {"fields": ["question_text", "feature"]}),
        (
            "Answer Validation",
            {"fields": ["case_sensitive", "use_fuzzy_comparison", "fuzzy_threshold"]},
        ),
    ]
    inlines = [QuestionAnswerInline]

    list_display = ["question_text"]
    search_fields = ["question_text"]


# Register the models with their respective classes.
admin.site.register(LocationsAppSettings, LocationAppSettingsAdmin)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(FeatureInstance, FeatureInstanceAdmin)

admin.site.register(QuestionFeature, QuestionFeatureAdmin)

admin.site.register(Map3DChunk, Map3DChunkAdmin)  # Only for dev Gamekeeper doesn't need
admin.site.register(FeatureInstanceTileMap)  # Only for dev Gamekeeper
# doesn't need
