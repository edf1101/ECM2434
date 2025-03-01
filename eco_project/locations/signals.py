"""
Signals for the Locations app.
Signals are an action that gets triggered when a certain event occurs.
These signals are used to update the min and max values of the lat/lon and world x/y/z of the
LocationsAppSettings singleton instance whenever a Map3DChunk instance is saved or deleted.
"""
from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver
from .models import Map3DChunk, LocationsAppSettings, FeatureInstance, FeatureInstanceTileMap, \
    Map3DChunk
from django.db.models import Min, Max
import sys


@receiver(post_save, sender=FeatureInstance)
@receiver(post_save, sender=LocationsAppSettings)
def update_feature_instance_qr_code(sender, instance, progress_bar=False, **kwargs) -> None:
    """
    Update the QR code of a FeatureInstance or all FeatureInstances.

    :param sender: The sender of the signal (should be FeatureInstance or LocationsAppSettings)
    :param instance: The instance of the sender
    :param progress_bar: Whether to display a progress bar
    """
    # If this save is triggered by an update_qr_code call skip to avoid infinite recursion.
    if hasattr(instance, '_skip_qr_update') and instance._skip_qr_update:
        return
    # If the sender is FeatureInstance, update only that instance this fixes infinite recursion
    if sender == FeatureInstance:
        instance._skip_qr_update = True
        instance.update_qr_code(skip_signal=True)
        instance._skip_qr_update = False
    else:
        for ind, feature_instance in enumerate(FeatureInstance.objects.all()):
            # print(f'created QR code for feature instance {feature_instance}')

            feature_instance._skip_qr_update = True
            feature_instance.update_qr_code(skip_signal=True)
            feature_instance._skip_qr_update = False

            length = FeatureInstance.objects.all().count()
            per = int(20 * (1 + ind) / length)  # how many # to draw
            if progress_bar:
                sys.stdout.write(  # draw a progress bar
                    f'\r[{"#" * per}{" " * (20 - per)}] {(1 + ind)}/{length}')
                sys.stdout.flush()
        if progress_bar:
            sys.stdout.write('\r\n')
            sys.stdout.flush()


@receiver(post_save, sender=Map3DChunk)
@receiver(post_delete, sender=Map3DChunk)
def update_min_max_pos(sender, instance, **kwargs) -> None:
    """
    Update the min and max values of the lat/lon and world x/y/z of the
    LocationsAppSettings singleton instance.
    """
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
    else:
        # Calculate aggregates in one go to avoid multiple queries if possible.
        aggregates = Map3DChunk.objects.aggregate(
            min_lat=Min('bottom_left_lat'),
            max_lat=Max('top_right_lat'),
            min_lon=Min('bottom_left_lon'),
            max_lon=Max('top_right_lon'),
            min_world_x=Min('bottom_left_x'),
            max_world_x=Max('top_right_x'),
            min_world_y=Min('bottom_left_y'),
            max_world_y=Max('top_right_y'),
            min_world_z=Min('bottom_left_z'),
            max_world_z=Max('top_right_z'),
        )
        settings = LocationsAppSettings.get_instance()
        settings.min_lat = aggregates['min_lat']
        settings.max_lat = aggregates['max_lat']
        settings.min_lon = aggregates['min_lon']
        settings.max_lon = aggregates['max_lon']
        settings.min_world_x = aggregates['min_world_x']
        settings.max_world_x = aggregates['max_world_x']
        settings.min_world_y = aggregates['min_world_y']
        settings.max_world_y = aggregates['max_world_y']
        settings.min_world_z = aggregates['min_world_z']
        settings.max_world_z = aggregates['max_world_z']

    # Set the flag to skip QR code updates when saving the settings.
    settings._skip_qr_update = True
    settings.save()
    # Optionally, remove the attribute so future saves behave normally.
    del settings._skip_qr_update


@receiver(post_save, sender=FeatureInstance)
@receiver(post_delete, sender=FeatureInstance)
@receiver(post_save, sender=Map3DChunk)
@receiver(post_delete, sender=Map3DChunk)
def update_tile_feature_map(sender, instance, **kwargs) -> None:
    """
    When a FeatureInstance or Map3DChunk is changed or deleted,
    clear and rebuild the tile feature map.

    This map shows which features reside in which map chunks.
    """
    # clear the existing tile feature map.
    FeatureInstanceTileMap.objects.all().delete()

    for feature in FeatureInstance.objects.all():
        # use filter not loop for speed. Check it is inside chunk geodesic bounds
        matching_chunks = Map3DChunk.objects.filter(
            bottom_left_lat__lte=feature.latitude,
            top_right_lat__gte=feature.latitude,
            bottom_left_lon__lte=feature.longitude,
            top_right_lon__gte=feature.longitude,
        )

        for chunk in matching_chunks:  # add all matching pairs to the mapping
            FeatureInstanceTileMap.objects.create(
                feature_instance=feature,
                map_chunk=chunk
            )
