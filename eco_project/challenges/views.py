"""
This module contains the challenges views
"""
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from locations.models import LocationsAppSettings
from .challenge_helpers import get_features_near
from .models import Quiz, QuizAttempt


def challenges_home(request) -> HttpResponse:
    """
    This view renders the home page.

    @param request: The request from the user.
    @return: The rendered home page.
    """

    # get nearby location features
    # get user location if logged in else get default locations
    lat = LocationsAppSettings.get_instance().default_lat
    lon = LocationsAppSettings.get_instance().default_lon
    if request.user.is_authenticated:
        lat = request.user.profile.latitude
        lon = request.user.profile.longitude

    nearby_features = list(get_features_near(lat, lon))

    # get all the quizzes
    quizzes = []
    for quiz in Quiz.objects.all():
        quizzes.append({
            'title': quiz.title,
            'points': quiz.total_points,
            'url': reverse('challenges:quiz_detail', kwargs={'quiz_id': quiz.id})  # Generate URL
        })
    context = {
        "nearby_features": nearby_features,
        "quizzes": quizzes,
    }

    return render(request, 'challenges/challenges_home.html', context=context)


def quiz_detail(request: HttpRequest, quiz_id: int) -> HttpResponse:
    """
    This view renders the quiz page.

    @param request: The request from the user.
    @param quiz_id: The id of the quiz.
    @return: The rendered quiz page.
    """

    # get the quiz object and its questions
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.order_by('id').all()

    # for each question index give it a letter (ABC...) and attach the choices
    quiz_data = []
    for question in questions:
        choices = question.choices.order_by('id').all()
        choices_with_letters = []
        for i, choice in enumerate(choices):
            letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i]
            choices_with_letters.append({'letter': letter, 'choice': choice})
        quiz_data.append({'question': question, 'choices': choices_with_letters})

    # check if the user is logged in and if so if they have attempted the quiz
    attempt = None
    if request.user.is_authenticated:
        try:
            attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz)
            # If they have attempted the quiz attach their answers
            if attempt:
                for i, item in enumerate(quiz_data):
                    item['user_answer'] = attempt.answers[i] if i < len(attempt.answers) else None
        except QuizAttempt.DoesNotExist:
            attempt = None

    return render(request, "challenges/quiz.html", {
        "quiz": quiz,
        "quiz_data": quiz_data,
        "attempt": attempt,
        "user_is_authenticated": request.user.is_authenticated,
    })
