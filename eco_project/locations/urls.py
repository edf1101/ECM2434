from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.base_locations, name="base"),
    path('reached/<slug:slug>', views.individual_feature_page, name="individual-feature"),
    path('education/', views.generic_feature_list, name="generic-feature-list"),
    path('education/<int:id>', views.generic_feature_page, name="generic-feature"),
]
