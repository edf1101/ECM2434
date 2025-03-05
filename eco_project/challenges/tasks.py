"""
This module contains tasks that are called by the scheduler.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.utils import timezone
from datetime import timedelta
from .models import Streak, get_current_window, UserFeatureReach
from .challenge_helpers import get_interval
from django.apps import apps




def update_challenges() -> None:
    """
    Gets called every 1m by the scheduler to update any time dependent challenges.

    @return: None
    """
    reset_missed_streaks()
    cleanup_user_feature_reaches()


def reset_missed_streaks() -> None:
    """
    Checks all Streak objects and resets raw_count for users who missed their check-in window.
    The window is determined by the interval (from StreakSettings or default to 1 day).

    @return: None
    """
    now_time = timezone.now()

    interval = get_interval()

    # get current window
    current_window_start, _ = get_current_window(now_time, interval)
    previous_window_start = current_window_start - interval

    count_reset = 0
    for streak in Streak.objects.all():  # go through all streaks and reset if out of window
        if streak.last_window not in [
            previous_window_start,
            current_window_start]:
            streak.raw_count = 0
            streak.save(update_fields=["raw_count"])
            count_reset += 1


def cleanup_user_feature_reaches() -> None:
    """
    Deletes any UserFeatureReach record that is in a past window.

    @return: None
    """
    now_time = timezone.now()

    current_window_start, _ = get_current_window(now_time, get_interval())

    # Delete all records where reached_at is before the start of the current
    UserFeatureReach.objects.filter(reached_at__lt=current_window_start).delete()



def update_pet_health():
    Pet = apps.get_model('pets', 'Pet')
    now = timezone.now()
    time_threshold = now - timedelta(minutes=1)  # Set to 1 day; adjust as needed

    pets = Pet.objects.filter(created_at__lte=time_threshold)
    for pet in pets:
        # Calculate new health by reducing current health by 5%
        new_health = int(pet.health * 0.95)
        # Ensure the health doesn't go below 0
        pet.health = max(0, new_health)
        pet.save()