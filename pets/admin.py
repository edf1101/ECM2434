from django.contrib import admin
from .models import PetType, Pet

admin.site.register(PetType)
admin.site.register(Pet)