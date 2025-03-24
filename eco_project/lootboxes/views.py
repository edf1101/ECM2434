"""
This module contains the views for the lootboxes app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

import random
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from .spinner import handle_result, WHEEL_OPTIONS, OPTION_PROBABILITIES


def wheel_view(request: HttpRequest) -> HttpResponse:
    """
    Renders the actual spinning wheel page.

    :param request: The HTTP request object.
    :return: The HTTP response object.
    """
    return render(
        request,
        'lootboxes/spin.html',
        context={
            'options': WHEEL_OPTIONS,
            'pet_bucks': request.user.profile.pet_bucks
        }
    )


@require_POST
def spin_wheel(request: HttpRequest) -> JsonResponse:
    """
    API endpoint that returns the result of spinning the wheel, or an error if the user cant
    afford to spin the wheel.

    :param request: The HTTP request object.
    :return: The JSON response object.
    """

    if request.user.profile.pet_bucks < 5:  # Check if the user can afford it
        return JsonResponse({'error': "Insufficient pet bucks."}, status=400)

    request.user.profile.pet_bucks -= 5  # pay the fee
    request.user.profile.save()

    # Choose a result
    result = random.choices(WHEEL_OPTIONS, weights=OPTION_PROBABILITIES, k=1)[0]
    handle_result(result, request.user)  # Handle the result

    return JsonResponse({
        'result': result,
        'options': WHEEL_OPTIONS,
        'pet_bucks': request.user.profile.pet_bucks
    })
