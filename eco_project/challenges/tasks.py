"""
This module contains tasks that are called by the scheduler.
"""
from datetime import timedelta

from django.utils import timezone

from .models import Streak, get_current_window, ChallengeSettings, UserFeatureReach


def update_challenges() -> None:
    """
    Gets called every 1m by the scheduler to update any time dependent challenges.
    """
    reset_missed_streaks()
    cleanup_user_feature_reaches()


def reset_missed_streaks() -> None:
    """
    Checks all Streak objects and resets raw_count for users who missed their check-in window.
    The window is determined by the interval (from StreakSettings or default to 1 day).
    """
    now_time = timezone.now()

    try:
        settings_obj = ChallengeSettings.objects.first()
        interval = settings_obj.interval if settings_obj else timedelta(days=1)
    except Exception:
        interval = timedelta(days=1)

    current_window_start, _ = get_current_window(now_time, interval)
    previous_window_start = current_window_start - interval

    count_reset = 0
    for streak in Streak.objects.all():
        if streak.last_window not in [previous_window_start, current_window_start]:
            streak.raw_count = 0
            streak.save(update_fields=['raw_count'])
            count_reset += 1


def cleanup_user_feature_reaches() -> None:
    """
    Deletes any UserFeatureReach record that is in a past window.
    """
    now_time = timezone.now()
    try:
        settings_obj = ChallengeSettings.objects.first()
        interval = settings_obj.interval if settings_obj else timedelta(days=1)
    except Exception:
        interval = timedelta(days=1)

    current_window_start, _ = get_current_window(now_time, interval)

    # Delete all records where reached_at is before the start of the current window.
    deleted_count, _ = UserFeatureReach.objects.filter(reached_at__lt=current_window_start).delete()
