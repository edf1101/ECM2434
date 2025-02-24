"""
This module is stores helper functions to deal with challenges.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from datetime import timedelta
from math import log2

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from locations.chunk_handling import haversine
from locations.models import FeatureInstance

User = get_user_model()


def get_interval() -> timedelta:
    """
    Get the interval for the streaks.

    @return: The interval for the streaks.
    """
    # pylint: disable=import-outside-toplevel
    from .models import ChallengeSettings
    try:
        settings_obj = ChallengeSettings.objects.first()
        interval = settings_obj.interval if settings_obj else timedelta(days=1)
    except ChallengeSettings.DoesNotExist:
        interval = timedelta(days=1)
    return interval


def get_current_window(now_time, interval):
    """
    Buckets the current time into fixed windows.
    For example, if interval is 1 day, returns the start and end of the current day.

    @param now_time: The current time.
    @param interval: The size of the window.
    @return: A tuple of (window_start, window_end).
    """
    base = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_base = (now_time - base).total_seconds()
    interval_seconds = interval.total_seconds()
    window_index = int(seconds_since_base // interval_seconds)
    window_start = base + timedelta(seconds=window_index * interval_seconds)
    window_end = window_start + interval
    return window_start, window_end


def streak_to_points(streak_count: int) -> int:
    """
    Given a streak count, returns the number of points that should be awarded.

    @param streak_count: The number of days in the streak.
    @return: The number of points to award.
    """
    return int(log2(streak_count) + 1)


def user_in_range_of_feature(
        user: User, feature_inst: FeatureInstance, range_dist: int = 100) -> bool:
    """
    Checks if a user is within the range of a feature.

    @param user: The user to check.
    @param feature_inst: The feature to check.
    @param range_dist: The range to check in meters.
    @return: True if the user is in range, False otherwise.
    """

    if not settings.CHECK_USER_CHALLENGE_RANGE:
        return True

    # Get the user's location
    user_lon = user.profile.longitude
    user_lat = user.profile.latitude

    # get the feature's location
    feature_lon = feature_inst.longitude
    feature_lat = feature_inst.latitude

    # Calculate the distance between the user and the feature
    dist = haversine(feature_lat, feature_lon, user_lat, user_lon)
    return dist <= range_dist


def user_already_reached_in_window(
        user: User, feature_inst: FeatureInstance, extra="", update=True
) -> bool:
    """
    Check if a user has already reached the feature in the current window.

    @param user: The user to check.
    @param feature_inst: The feature instance to check.
    @param extra: An extra field to check.
    @param update: If True, will add a record if the user has not already reached the feature.
    @return: True if the user has reached the feature in the current window, False otherwise.
    """
    # pylint: disable=import-outside-toplevel
    from .models import UserFeatureReach, ChallengeSettings  # avoid circular import

    # Get the current challenge settings for the interval
    settings_obj = ChallengeSettings.get_solo()
    interval = settings_obj.interval

    now_time = timezone.now()
    window_start, window_end = get_current_window(now_time, interval)

    already_reached = UserFeatureReach.objects.filter(
        user=user,
        feature_instance=feature_inst,
        reached_at__gte=window_start,
        reached_at__lt=window_end,
        extra=extra,
    ).exists()

    if not already_reached:
        # add record and return true
        if update:
            UserFeatureReach.objects.create(
                user=user, feature_instance=feature_inst, extra=extra
            )
        return False

    return True


def user_reached_feature(user: User, feature_inst: FeatureInstance) -> None:
    """
    Does some things when a user reaches a feature.

    @param user: The user to check.
    @param feature_inst: The feature to check.
    """

    if not user_in_range_of_feature(user, feature_inst):
        print("User not in range of feature")
        return

    if user_already_reached_in_window(user, feature_inst):
        print("User already reached feature in window")
        return

    # needed to avoid circular import
    # pylint: disable=import-outside-toplevel
    from .models import ChallengeSettings

    points_for_feature = ChallengeSettings.get_solo().reached_feature_points

    user.profile.points += points_for_feature
    user.profile.save()
