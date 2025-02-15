"""
Admin panel configuration for Streak and StreakSettings models.
"""

from django.contrib import admin

from .models import Streak, ChallengeSettings


class StreakAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Streak model.
    """
    list_display = ('user', 'raw_count', 'last_window', 'effective_streak', 'running_out')
    readonly_fields = ('effective_streak', 'running_out')


class ChallengeSettingsAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Challenge settings model.
    """
    list_display = ('interval',)
    fieldsets = (
        ('Streak Settings', {'fields': ('interval',)}),
    )


admin.site.register(Streak, StreakAdmin)
admin.site.register(ChallengeSettings, ChallengeSettingsAdmin)
