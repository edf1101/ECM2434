"""
This file deals with displaying user app related models in the admin panel.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    This is the inline class for the Profile model, it goes inside the user admin view.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

    # The fields that will be displayed in the inline
    fieldsets = (
        ('Profile', {'fields': ('bio',)}),
        ('Scoring', {'fields': ('points',)}),
        ('Location', {'fields': ('latitude', 'longitude')}),
    )


class CustomUserAdmin(BaseUserAdmin):
    """
    This is the custom user admin class page that has been modified to only show the fields we want.
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name'),

        }),
    )

    list_display = (
        'username', 'first_name', 'last_name', 'is_staff',
        'profile_points')  # Only these fields will be displayed

    inlines = (ProfileInline,)

    def profile_points(self, obj):
        """
        This function is used to display the points of the user in the admin panel.
        """

        return obj.profile.points if hasattr(obj, 'profile') else 'N/A'

    profile_points.short_description = 'Points'

# deregister the default model and replace with our own.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
