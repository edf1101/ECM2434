"""
Signals for the Locations app.
Signals are an action that gets triggered when a certain event occurs.
These signals are used to update the min and max values of the lat/lon and world x/y/z of the
LocationsAppSettings singleton instance whenever a Map3DChunk instance is saved or deleted.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Map3DChunk, LocationsAppSettings
from django.db.models import Min, Max


@receiver(post_save, sender=Map3DChunk)
@receiver(post_delete, sender=Map3DChunk)
def update_min_max_pos(sender, instance, **kwargs) -> None:
    """
    Update the min and max values of the lat/lon and world x/y/z of the
    LocationsAppSettings singleton instance.

    :param sender: The sender of the signal (should be Map3DChunk)
    :param instance: The instance of the sender
    :param kwargs: Usually None
    :return: None
    """

    # If no Map3DChunks exist, set defaults for LocationsAppSettings this prevents errors
    # during deletion of all Map3DChunk instances
    if not Map3DChunk.objects.exists():
        settings = LocationsAppSettings.get_instance()
        settings.min_lat = 0.0
        settings.max_lat = 0.0
        settings.min_lon = 0.0
        settings.max_lon = 0.0
        settings.min_world_x = 0.0
        settings.max_world_x = 0.0
        settings.min_world_y = 0.0
        settings.max_world_y = 0.0
        settings.min_world_z = 0.0
        settings.max_world_z = 0.0
        settings.save()
    else:
        # Calculate the min and max values from all Map3DChunk instances
        min_lat_value = Map3DChunk.objects.aggregate(Min('center_lat'))['center_lat__min']
        max_lat_value = Map3DChunk.objects.aggregate(Max('center_lat'))['center_lat__max']
        min_lon_value = Map3DChunk.objects.aggregate(Min('center_lon'))['center_lon__min']
        max_lon_value = Map3DChunk.objects.aggregate(Max('center_lon'))['center_lon__max']

        min_world_x_value = Map3DChunk.objects.aggregate(Min('bottom_left_x'))['bottom_left_x__min']
        max_world_x_value = Map3DChunk.objects.aggregate(Max('top_right_x'))['top_right_x__max']
        min_world_y_value = Map3DChunk.objects.aggregate(Min('bottom_left_y'))['bottom_left_y__min']
        max_world_y_value = Map3DChunk.objects.aggregate(Max('top_right_y'))['top_right_y__max']
        min_world_z_value = Map3DChunk.objects.aggregate(Min('bottom_left_z'))['bottom_left_z__min']
        max_world_z_value = Map3DChunk.objects.aggregate(Max('top_right_z'))['top_right_z__max']

        # Get or create the singleton LocationsAppSettings instance
        settings = LocationsAppSettings.get_instance()

        # Update the settings with the new min/max values
        settings.min_lat = min_lat_value
        settings.max_lat = max_lat_value
        settings.min_lon = min_lon_value
        settings.max_lon = max_lon_value

        settings.min_world_x = min_world_x_value
        settings.max_world_x = max_world_x_value
        settings.min_world_y = min_world_y_value
        settings.max_world_y = max_world_y_value
        settings.min_world_z = min_world_z_value
        settings.max_world_z = max_world_z_value

        # Save the updated settings
        settings.save()
