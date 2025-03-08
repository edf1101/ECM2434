from django.contrib import admin

from .models import ReactionType, UserPhoto, UserPhotoReaction

# Register your models here.
admin.site.register(ReactionType)
admin.site.register(UserPhoto)
admin.site.register(UserPhotoReaction)