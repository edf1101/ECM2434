from django.urls import path
from . import views
from . import api

app_name = 'pets'

urlpatterns = [
    path('mypet/', views.view_pet, name="mypet"),
    path('api/get_pet_data/<str:username>/', api.get_pet_data, name="get_pet_data"),
]
