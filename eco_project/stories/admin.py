"""
This file is used to register the models in the Django admin interface.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib import admin

from .models import ReactionType, UserPhoto, UserPhotoReaction

# Register your models here.
admin.site.register(ReactionType)
admin.site.register(UserPhoto)
admin.site.register(UserPhotoReaction)
