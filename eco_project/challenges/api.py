"""
This file contains the API endpoints for the challenges app.
@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.http import JsonResponse
from django.http.request import HttpRequest
from django.utils import timezone
from locations.models import QuestionFeature
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .challenge_helpers import (
    get_current_window,
    streak_to_points,
    user_in_range_of_feature,
    user_already_reached_in_window,
    get_interval,
    get_features_near
)

from .models import Streak, ChallengeSettings, Quiz, QuizAttempt


@api_view(["POST"])
def collect_streak(request) -> Response:
    """
    this gets called when the user wants to collect their streak

    @param request: The POST request object.
    @return: A JSON response with a message to the front end
    """
    user = request.user

    # If user is not authenticated, return a message gracefully.
    if not user.is_authenticated:
        return Response({"message": "Authentication required."})

    streak, _ = Streak.objects.get_or_create(user=user)
    now_time = timezone.now()

    interval = get_interval()

    current_window_start, _ = get_current_window(now_time, interval)
    previous_window_start = current_window_start - interval

    # If already collected in this window, return a message.
    if streak.last_window == current_window_start:
        return Response(
            {
                "message": "You have already collected your streak for this window.",
                "streak": streak.effective_streak,  # computed value based on raw_count
            }
        )

    # If the last check-in was in the immediately preceding window, increment
    # streak.
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

    return Response({"message": "Streak updated!",
                     "streak": streak.effective_streak})


@api_view(["POST"])
def submit_answer_api(request) -> Response:
    """
    This function handles the submission of answers to questions.

    @param request: The POST request object. Need a JSON object with 'answer'
    and 'question_id' keys.
    @return: A JSON response with a message to the front end
    """

    signed_in = request.user and request.user.is_authenticated

    answer_text = request.data.get("answer")
    question_id = request.data.get("question_id")

    try:
        question = QuestionFeature.objects.get(id=question_id)
    except QuestionFeature.DoesNotExist:
        return Response({"error": "Question not found"}, status=404)

    valid = question.is_valid_answer(answer_text)

    if (
            not signed_in
    ):  # handle non signed in users so they can still learn but just not get points
        return Response(
            {
                "message": f'The answer is {"correct" if valid else "incorrect"} but'
                           f' you are not signed in',
            }
        )

    # check if in range
    if not user_in_range_of_feature(request.user, question.feature):
        return Response(
            {
                "message": "You are not in range of the feature",
            }
        )

    if user_already_reached_in_window(
            request.user,
            question.feature,
            extra="question"):
        return Response(
            {
                "message": "You have already reached this feature in this window",
            }
        )

    if valid:
        # get how many point per question feature from challenge settings

        points_per_q = ChallengeSettings.get_solo().question_feature_points
        request.user.profile.points += points_per_q
        request.user.profile.save()

    # Return response with required info
    return Response(
        {
            "message": f'The answer is {"correct" if valid else "incorrect"}',
        }
    )


def nearest_challenges_api(request) -> JsonResponse:
    """
    Returns up to 10 nearest challenges as JSON, sorted by distance.

    @param request: The GET request object.
    @return: A JSON response with a list of challenges
    """
    challenges = []
    if (
            not request.user.is_authenticated
    ):  # if user is not authenticated, return empty list
        return JsonResponse({"challenges": challenges})

    # Find all the challenges that the user has not yet reached
    # and are within a certain distance of the user
    current_user_lat = request.user.profile.latitude
    current_user_long = request.user.profile.longitude
    challenges = get_features_near(current_user_lat, current_user_long, request.user)
    return JsonResponse({"challenges": challenges})


@api_view(['POST'])
def score_quiz(request: HttpRequest) -> Response:
    """
    This API endpoint handles when a quiz is submitted and grades it.

    @param request: The POST request object.
    @return: A response with a message to the front end.
    """

    # Get the quiz id and the user's answers
    quiz_id = request.data.get('quiz_id')
    answers = request.data.get('answers')

    if quiz_id is None or answers is None:  # Error check bad answers
        return Response(
            {"error": "Both 'quiz_id' and 'answers' are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        quiz = Quiz.objects.get(pk=quiz_id) # Get the quiz
    except Quiz.DoesNotExist:
        return Response(
            {"error": "Quiz not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    questions = quiz.questions.order_by('id').all()  # get the user answers and the questions
    if len(answers) != questions.count():
        return Response(
            {"error": "The number of answers provided does not match the number of questions."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # go through each question and check if the answer is correct
    correct_count = 0
    for idx, question in enumerate(questions):
        choices = list(question.choices.order_by('id').all())
        correct_letter = None
        for i, choice in enumerate(choices):
            if choice.is_correct:
                correct_letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i]
                break
        if answers[idx] == correct_letter:
            correct_count += 1

    # calculate the score
    total_questions = questions.count()
    percentage = int(correct_count / total_questions * 100)
    points = int(correct_count / total_questions * quiz.total_points)

    # If the user is logged in and the attempt is new, save the attempt and give the user points
    if request.user.is_authenticated:
        _, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'answers': answers, 'score': percentage}
        )
        if created:
            request.user.profile.points += points
            request.user.profile.save()

            if percentage > 80:
                reward_health = 20  
                pet = request.user.pets.first() 
                if pet:
                    pet.health = min(pet.health + reward_health, 100)
                    pet.save()

            

    return Response({
        "message": f"You got {percentage}% correct. Total points awarded: {points}",
    })
