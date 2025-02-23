from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('mypet/', views.view_pet, name="mypet"),
]
