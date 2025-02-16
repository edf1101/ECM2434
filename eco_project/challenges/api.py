from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import timedelta
from django.conf import settings

# Import your models and helper
from .models import Streak, ChallengeSettings  # adjust import as needed
from .streaks import get_current_window  # helper to bucket time into windows


@api_view(['POST'])
def collect_streak(request):
    user = request.user

    # If user is not authenticated, return a message gracefully.
    if not user.is_authenticated:
        return Response({"message": "Authentication required."})

    streak, created = Streak.objects.get_or_create(user=user)
    now_time = timezone.now()

    # Determine the streak interval:
    # Try to get it from the DB; if not, fallback to a default from settings.
    try:
        settings_obj = ChallengeSettings.objects.first()
        interval = settings_obj.interval if settings_obj else timedelta(days=1)
    except Exception:
        interval = getattr(settings, "STREAK_INTERVAL", timedelta(days=1))

    current_window_start, _ = get_current_window(now_time, interval)
    previous_window_start = current_window_start - interval

    # If already collected in this window, return a message.
    if streak.last_window == current_window_start:
        return Response({
            "message": "You have already collected your streak for this window.",
            "streak": streak.effective_streak  # computed value based on raw_count
        })

    # If the last check-in was in the immediately preceding window, increment streak.
    if streak.last_window == previous_window_start:
        streak.raw_count += 1
    else:
        # Otherwise, the streak is broken; start over.
        streak.raw_count = 1

    # Update the last_window to the start of the current window.
    streak.last_window = current_window_start
    streak.save()

    return Response({
        "message": "Streak updated!",
        "streak": streak.effective_streak
    })
