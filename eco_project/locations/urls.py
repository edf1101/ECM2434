"""
This file contains the URL patterns for the locations app.
"""
from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.base_locations, name="base"),
    path('map/', views.test_map, name="map"),
    path('reached/<slug:slug>', views.individual_feature_page, name="individual-feature"),
    path('education/', views.generic_feature_list, name="generic-feature-list"),
    path('education/<int:id_arg>', views.generic_feature_page, name="generic-feature"),
    path('api/nearby-tiles/', views.nearby_tiles, name='nearby-tiles'),
    path('api/map_data/', views.api_get_map_data, name='map-data'),
]
