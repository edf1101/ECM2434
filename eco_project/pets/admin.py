"""
This file is used to register the models in the admin panel.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib import admin

from .models import PetType, Pet, CosmeticType, Cosmetic

admin.site.register(PetType)
admin.site.register(Pet)
admin.site.register(CosmeticType)
admin.site.register(Cosmetic)
