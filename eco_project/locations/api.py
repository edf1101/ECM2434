from .models import FeatureInstance, FeatureType, Map3DChunk, LocationsAppSettings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .chunk_handling import get_nearby_tiles
from random import uniform
import math


@api_view(['GET'])
def nearby_tiles(request) -> Response:
    """
    This function returns a list of nearby 3D map tiles given a latitude, longitude and distance.

    :param request: The get request object that hopefully contains lat, lon and distance.
    :return:
    """
    try:
        # Get the lat, lon and distance from the GET request
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        max_distance = float(request.GET.get("distance", 100))

        tiles = get_nearby_tiles(lat, lon, max_distance)  # Get tiles

        # Create a response with the list of tiles
        response_data = [
            {"id": tile.id, "file": tile.file.url, "lat": tile.center_lat, "lon": tile.center_lon}
            for tile in tiles
        ]

        return Response(response_data, status=200)

    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)


@api_view(['GET'])
def api_get_map_data(request) -> Response:
    """
    This function returns the map settings data for the 3D map.

    :param request: The get request object. No data to read here.
    :return: The map settings data in JSON format.
    """

    # Get the map settings data from the LocationsAppSettings model
    min_lat = LocationsAppSettings.get_instance().min_lat
    max_lat = LocationsAppSettings.get_instance().max_lat
    min_lon = LocationsAppSettings.get_instance().min_lon
    max_lon = LocationsAppSettings.get_instance().max_lon

    min_x = LocationsAppSettings.get_instance().min_world_x
    max_x = LocationsAppSettings.get_instance().max_world_x

    min_y = LocationsAppSettings.get_instance().min_world_y
    max_y = LocationsAppSettings.get_instance().max_world_y

    min_z = LocationsAppSettings.get_instance().min_world_z
    max_z = LocationsAppSettings.get_instance().max_world_z

    camera_map_url = LocationsAppSettings.get_instance().camera_z_map.url

    # Create a response with the map settings data
    response_data = [
        {"min_lat": min_lat, "max_lat": max_lat,
         "min_lon": min_lon, "max_lon": max_lon,
         "min_x": min_x, "max_x": max_x,
         "min_y": min_y, "max_y": max_y,
         "min_z": min_z, "max_z": max_z,
         "camera_map_url": camera_map_url}
    ]

    return Response(response_data, status=200)


@api_view(['GET'])
def get_current_location(request) -> Response:
    """
    This function returns a random location for the user that is not within 300m of the map's border.

    :param request: The GET request object. No data to read here.
    :return: The current location of the user as a JSON response.
    """
    # For demo, choose a random lat lon within the map bounds, but not within 300m of the border.
    settings = LocationsAppSettings.get_instance()
    min_lat = settings.min_lat
    max_lat = settings.max_lat
    min_lon = settings.min_lon
    max_lon = settings.max_lon

    # Calculate margin in degrees corresponding to 300 meters.
    # 1 degree of latitude is approximately 111 km.
    margin_lat = 300 / 111000  # in degrees

    # For longitude, the conversion factor depends on latitude.
    # Use the average latitude to compute the margin.
    avg_lat = (min_lat + max_lat) / 2.0
    margin_lon = 300 / (111000 * math.cos(math.radians(avg_lat)))

    dp = 5  # number of decimal places to round to

    # Choose a random latitude and longitude within the bounds, excluding the border margin.
    lat = round(uniform(min_lat + margin_lat, max_lat - margin_lat), dp)
    lon = round(uniform(min_lon + margin_lon, max_lon - margin_lon), dp)

    return Response({"lat": lat, "lon": lon}, status=200)
