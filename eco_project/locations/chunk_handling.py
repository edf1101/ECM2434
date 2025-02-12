"""
This module contains functions for handling 3D map tiles and other geodesic calculations.
"""
import math
from django.db.models import Q
from .models import Map3DChunk


def haversine(lat1, lon1, lat2, lon2):
    """
    The haversine formula is used for calculating the distance between two points on the Earth's
    surface in meters given their latitudes and longitudes.

    :param lat1: Input latitude 1 ie y1
    :param lon1: Input longitude 1 ie x1
    :param lat2: Input latitude 2 ie y2
    :param lon2: Input longitude 2 ie x2
    :return: The distance between the two points in meters
    """

    earth_rad = 6371000  # Earth's radius in meters
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(
        delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_rad * c  # Distance in meters


def get_nearby_tiles(lat, lon, max_distance_meters=100):
    """
    Get all 3D map chunks within a certain distance of a given latitude and longitude.

    :param lat: The input latitude  (y)
    :param lon: The input longitude (x)
    :param max_distance_meters: The maximum distance in meters to search for
     nearby tiles (default 100)
    :return: The list of nearby 3D map chunks
    """

    # Create a bounding box that the tiles center lat/lon must be within
    # Those bounds will be center + these offsets
    lat_offset = max_distance_meters / 111320  # 1 degree is roughly 111.32 km
    lon_offset = max_distance_meters / (111320 * math.cos(math.radians(lat)))

    # Filter using Q objects to get the chunks within bounds this is hopefully
    # lots faster than using a loop
    bounded_chunks = Map3DChunk.objects.filter(
        Q(center_lat__gte=lat - lat_offset) & Q(center_lat__lte=lat + lat_offset) &
        Q(center_lon__gte=lon - lon_offset) & Q(center_lon__lte=lon + lon_offset)
    )

    # Actually check the bounded chunks to see if they are within the max distance
    nearby_chunks = [
        chunk for chunk in bounded_chunks
        if haversine(lat, lon, chunk.center_lat, chunk.center_lon) <= max_distance_meters
    ]

    return nearby_chunks
