"""
This file contains the URL patterns for the locations app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.urls import path

from . import api
from . import views

app_name = "locations"

urlpatterns = [
    path("", views.base_locations, name="base"),
    path("reached/<slug:slug>", views.individual_feature_page, name="individual-feature"),
    path("education/<int:id_arg>", views.generic_feature_page, name="generic-feature"),
    path("api/nearby-tiles/", api.nearby_tiles, name="nearby-tiles"),
    path("api/map_data/", api.api_get_map_data, name="map-data"),
    path("api/get_location/", api.get_current_location, name="get-location"),
    path("api/get_feature_instances/", api.get_feature_instances, name="get-feature-instances", ),
    path("api/get_features_for_tile/", api.get_features_for_tiles, name="get-feature-for-tiles", ),
    path("api/validate_qr/", api.validate_qr, name="validate_qr"),
]
