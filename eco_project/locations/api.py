"""
This file contains the API endpoints for the Locations app

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import json

from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .chunk_handling import get_nearby_tiles
from .models import (
    FeatureInstance,
    Map3DChunk,
    LocationsAppSettings,
    FeatureInstanceTileMap,
)


@api_view(["GET"])
def nearby_tiles(request) -> Response:
    """
    This function returns a list of nearby 3D map tiles given a latitude, longitude and distance.

    @param request: The get request object that hopefully contains lat, lon and distance.
    @return: the JSON response containing the nearby tiles.
    """
    try:
        # Get the lat, lon and distance from the GET request
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        max_distance = float(request.GET.get("distance", 100))

        tiles = get_nearby_tiles(lat, lon, max_distance)  # Get tiles

        # Create a response with the list of tiles
        response_data = [
            {
                "id": tile.id,
                "file": tile.file.url,
                "lat": tile.center_lat,
                "lon": tile.center_lon,
            }
            for tile in tiles
        ]

        return Response(response_data, status=200)

    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)


@api_view(["GET"])
def get_features_for_tiles(request) -> Response:
    """
    Returns a dictionary where each key is a tile file URL and each value is a list of
    features on that tile. Each feature is represented by its latitude, longitude,
    and feature colour. Expects a GET parameter "tiles" with a comma-separated list of tile IDs.

    @param request: The GET request object.
    @return: The response containing the dictionary of features.
    """
    tiles_param = request.GET.get("tiles")
    if not tiles_param:
        return Response({"error": "No tiles provided."}, status=400)

    try:
        tile_ids = [int(i) for i in tiles_param.split(",")]
    except ValueError:
        return Response({"error": "Invalid tile IDs provided."}, status=400)

    # Get tile objects from the IDs
    tiles = Map3DChunk.objects.filter(id__in=tile_ids)

    # Build the response data dictionary: key = tile file URL, value = list of
    # feature details
    response_data = {}

    for tile in tiles:
        features_in_tile = []
        # Get the mapping objects for this tile
        tile_mappings = FeatureInstanceTileMap.objects.filter(map_chunk=tile)
        for mapping in tile_mappings:
            instance = mapping.feature_instance
            features_in_tile.append(
                {
                    "lat": instance.latitude,
                    "lon": instance.longitude,
                    "colour": instance.feature.colour,
                    "mesh_url": instance.feature.feature_mesh.url
                    if instance.feature.feature_mesh
                    else "None",
                }
            )
        response_data[tile.file.url] = features_in_tile

    return Response(response_data, status=200)


@api_view(["GET"])
def api_get_map_data(request) -> Response:
    """
    This function returns the map settings data for the 3D map.

    @param request: The get request object. No data to read here.
    @return: The map settings data in JSON format.
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

    bg_colour = LocationsAppSettings.get_instance().world_colour
    render_dist = LocationsAppSettings.get_instance().render_dist

    # Create a response with the map settings data
    response_data = [
        {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "min_z": min_z,
            "max_z": max_z,
            "camera_map_url": camera_map_url,
            "bg_colour": bg_colour,
            "render_dist": render_dist,
        }
    ]

    return Response(response_data, status=200)


@api_view(["GET"])
def get_current_location(request) -> Response:
    """
    This function returns a random location for the user that is not within 300m of
     the map's border.

    @param request: The GET request object. No data to read here.
    @return The current location of the user as a JSON response.
    """

    # get default lat and lon
    default_lat = LocationsAppSettings.get_instance().default_lat
    default_lon = LocationsAppSettings.get_instance().default_lon
    # get the user's current location from the user object
    if request.user.is_authenticated:
        current_user = request.user
        lat = current_user.profile.latitude
        lon = current_user.profile.longitude
    else:  # if the user is not signed in, return main campus location
        lat, lon = default_lat, default_lon

    # find out if user is within map bounds
    min_lat = LocationsAppSettings.get_instance().min_lat
    max_lat = LocationsAppSettings.get_instance().max_lat
    min_lon = LocationsAppSettings.get_instance().min_lon
    max_lon = LocationsAppSettings.get_instance().max_lon
    in_bounds = min_lat < lat < max_lat and min_lon < lon < max_lon

    if not in_bounds:  # if not in bounds return main campus location
        lat, lon = default_lat, default_lon

    return Response({"lat": lat, "lon": lon}, status=200)


@api_view(["GET"])
def get_feature_instances(request) -> Response:
    """
    This function returns all feature instances in the database.

    @param request: The GET request object. No data to read here.
    @return: A JSON response containing all feature instances.
    """
    feature_instances = FeatureInstance.objects.all()

    # for each feature instance, return its lat, lon, featureType.colour
    response_data = [
        {
            "lat": instance.latitude,
            "lon": instance.longitude,
            "colour": instance.feature.colour,
        }
        for instance in feature_instances
    ]

    return Response(response_data, status=200)


@require_POST
def validate_qr(request):
    """
    Validates a QR code link to a feature and redirects to its page if valid.
    """
    try:
        # Parse the JSON data
        data = json.loads(request.body)
        qr_code = data.get("qr_code", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID_REQUEST", "message": "Invalid JSON"}, status=400)

    # If no QR code is provided
    if not qr_code:
        return JsonResponse({"error": "INVALID_QR", "message": "Empty QR code"}, status=400)

    # Try to extract the last part of the QR code
    try:
        # Split by '/' and get the last non-empty part
        strip_qr = list(filter(None, qr_code.split("/")))[-1] if '/' in qr_code else qr_code
    except IndexError:
        strip_qr = qr_code

    # Try to find the feature instance
    try:
        FeatureInstance.objects.get(slug=strip_qr)

        # If found, redirect to the feature's page
        target_url = reverse(
            "locations:individual-feature",
            kwargs={"slug": strip_qr}
        )
        return redirect(target_url)

    except FeatureInstance.DoesNotExist:
        # Log the unsuccessful QR code for debugging
        print(f"QR Code validation failed for: {strip_qr}")
        return JsonResponse({
            "error": "INVALID_QR",
            "message": "No matching location found",
            "attempted_slug": strip_qr
        }, status=404)
