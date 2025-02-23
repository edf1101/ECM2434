from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse

# Import your models and helper
from .models import Streak, ChallengeSettings  # adjust import as needed
from .challenge_helpers import get_current_window, streak_to_points, user_in_range_of_feature, \
    user_already_reached_in_window
from locations.models import QuestionFeature, FeatureInstance
from locations.chunk_handling import haversine


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

    # add points to the user
    points_awarded = streak_to_points(streak.raw_count)
    user.profile.points += points_awarded
    user.profile.save()

    # Update the last_window to the start of the current window.
    streak.last_window = current_window_start
    streak.save()

    return Response({
        "message": "Streak updated!",
        "streak": streak.effective_streak
    })


@api_view(['POST'])
def submit_answer_api(request) -> Response:
    """
    This function handles the submission of answers to questions.

    :param request: The POST request object. Need a JSON object with 'answer'
    and 'question_id' keys.
    :return: A JSON response with a message to the front end
    """

    signed_in = request.user and request.user.is_authenticated

    answer_text = request.data.get('answer')
    question_id = request.data.get('question_id')

    try:
        question = QuestionFeature.objects.get(id=question_id)
    except QuestionFeature.DoesNotExist:
        return Response({'error': 'Question not found'}, status=404)

    valid = question.is_valid_answer(answer_text)

    if not signed_in:  # handle non signed in users so they can still learn but just not get points
        return Response({
            'message': f'The answer is {"correct" if valid else "incorrect"} but you are not signed in',
        })

    # check if in range
    if not user_in_range_of_feature(request.user, question.feature):
        return Response({
            'message': 'You are not in range of the feature',
        })

    if user_already_reached_in_window(request.user, question.feature, extra="question"):
        return Response({
            'message': 'You have already reached this feature in this window',
        })

    if valid:
        # get how many point per question feature from challenge settings

        points_per_q = ChallengeSettings.get_solo().question_feature_points
        request.user.profile.points += points_per_q
        request.user.profile.save()

    # Return response with required info
    return Response({
        'message': f'The answer is {"correct" if valid else "incorrect"}',
    })


def nearest_challenges_api(request):
    """
    Returns up to 10 nearest challenges as JSON, sorted by distance.
    In production, you’d query your database based on user location.
    """
    challenges = []
    if not request.user.is_authenticated:  # if user is not authenticated, return empty list
        return JsonResponse({"challenges": challenges})

    # Find all the challenges that the user has not yet reached
    # and are within a certain distance of the user
    current_user_lat = request.user.profile.latitude
    current_user_long = request.user.profile.longitude
    challenge_data: dict[FeatureInstance, str] = {}
    for feature in FeatureInstance.objects.all():
        if not user_already_reached_in_window(request.user, feature,update=False):
            dist = haversine(current_user_lat, current_user_long, feature.latitude,
                             feature.longitude)
            dist_str = f'{dist/1000.0:.2f}km away' if dist > 1 else f'{int(dist)}m away'
            challenge_data[feature] = dist_str

    # Sort the challenges by distance and get the 10 closest
    sorted_challenges = sorted(challenge_data.items(), key=lambda x: x[1])
    for feature, dist in sorted_challenges[:10]:
        challenges.append({
            "directions": dist,
            "description": feature.name,
        })
    return JsonResponse({"challenges": challenges})
