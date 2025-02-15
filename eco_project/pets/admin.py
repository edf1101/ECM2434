from django.contrib import admin

from .models import PetType, Pet, CosmeticType, Cosmetic

admin.site.register(PetType)
admin.site.register(Pet)
admin.site.register(CosmeticType)
admin.site.register(Cosmetic)