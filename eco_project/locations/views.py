"""
This module contains the views for the locations app.
"""
from django.shortcuts import render
from django.http import HttpResponse

from .models import FeatureInstance, FeatureType, Map3DChunk, LocationsAppSettings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .chunk_handling import get_nearby_tiles


def base_locations(request) -> HttpResponse:
    """
    This function returns the homepage for the locations app.

    :param request: The request object that gets passed to the view.
    :return: An HTTP webpage to render to the user.
    """
    return HttpResponse('Locations Homepage')


def test_map(request) -> HttpResponse:
    """
    This function returns a test map page for the locations app.

    :param request: The request object that gets passed to the view.
    :return: An HTTP webpage to render to the user.
    """

    # no context required as the tile data is loaded with GET requests
    return render(request, 'locations/test_map.html')


def individual_feature_page(request, slug) -> HttpResponse:
    """
    This function returns the page for a specific feature instance ie not a feature type.

    :param request: The request object that gets passed to the view.
    :param slug: The slug (unique url name) of the feature.
    :return: An HTTP webpage to render to the user.
    """
    feature_instance: FeatureInstance = FeatureInstance.objects.get(slug=slug)
    context = {'feature_instance': feature_instance}
    return render(request, 'locations/feature_instance.html', context)


def generic_feature_page(request, id_arg) -> HttpResponse:
    """
    This function returns the page for a generic feature type.
    Ie a generic Water fountain NOT a specific water fountain.

    :param request: The request object that gets passed to the view.
    :param id_arg: The id (PK) of the feature.
    :return: The HTTP webpage to render to the user.
    """
    feature_type: FeatureType = FeatureType.objects.get(id=id_arg)
    context = {'feature_type': feature_type}
    return render(request, 'locations/feature_type.html', context)


def generic_feature_list(request) -> HttpResponse:
    """
    This function returns a webpage that lists all the generic features with hyperlinks.

    :param request:  The request object that gets passed to the view.
    :return: An HTTP webpage to render to the user.
    """
    generic_features = FeatureType.objects.all()
    context = {'feature_type_list': generic_features}
    return render(request, 'locations/feature_type_list.html', context)


@api_view(['GET'])
def nearby_tiles(request):
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
def api_get_map_data(request):
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

    # Create a response with the map settings data
    response_data = [
        {"min_lat": min_lat, "max_lat": max_lat, "min_lon": min_lon, "max_lon": max_lon,
         "min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y}
    ]

    return Response(response_data, status=200)
