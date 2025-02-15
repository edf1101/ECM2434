"""
This file deals with displaying user app related models in the admin panel.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .forms import BadgeAdminForm, UserGroupForm
from .models import Profile, Badge, BadgeInstance, UserGroup


class BadgeInstanceInline(admin.TabularInline):
    """
    Inline for the BadgeInstance model to appear in the user admin.
    """
    model = BadgeInstance
    extra = 0  # No extra blank forms


class ProfileInline(admin.StackedInline):
    """
    Inline for the Profile model to appear in the user admin.
    """
    model = Profile
    can_delete = False
    extra = 0
    max_num = 1

    def has_add_permission(self, request, obj):
        """
        Prevent adding a new profile if one already exists.
        """
        if obj and hasattr(obj, 'profile'):
            return False
        return True


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom user admin that displays additional fields.
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
        'profile_points', 'badge_count'
    )

    inlines = (ProfileInline, BadgeInstanceInline)

    def get_inline_instances(self, request, obj=None):
        """
        When adding a new user, do not display inlines.
        This prevents duplicate profile creation.
        """
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def profile_points(self, obj):
        """
        Display the user's points from their profile.
        """
        return obj.profile.points if hasattr(obj, 'profile') else 'N/A'

    profile_points.short_description = 'Points'

    def badge_count(self, obj):
        """
        Display the number of badge instances associated with the user.
        """
        return obj.badgeinstance_set.count() if hasattr(obj, 'badgeinstance_set') else 'N/A'

    badge_count.short_description = 'Badges'


class BadgeAdmin(admin.ModelAdmin):
    """
    Admin for the Badge model.
    """
    model = Badge
    list_display = ('title', 'hover_text', 'rarity')
    form = BadgeAdminForm
    search_fields = ['title', 'rarity']


class UserGroupAdmin(admin.ModelAdmin):
    """
    Admin for the UserGroup model.
    """
    model = UserGroup
    readonly_fields = ('users_in_group',)
    list_display = ('code', 'users_in_group')
    search_fields = ['code']
    form = UserGroupForm


# Register Badge admin.
admin.site.register(Badge, BadgeAdmin)
admin.site.register(UserGroup, UserGroupAdmin)

# Replace the default User admin with our custom admin.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
