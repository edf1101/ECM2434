"""
This module is used to store the API endpoints for the pets app.
This includes the frontend calling get_pet_data(user) to get the data for a pet.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the user model


@require_POST
def get_pet_data(request, username) -> JsonResponse:
    """
    This function is used to get the data for a pet.

    @param request: The request object.
    @param username: The username of the user to get the pet data for.
    @return: A JsonResponse containing the pet data.
    """
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    pet = target_user.pets.first()  # For sprint 1 users will only have 1 pet
    if not pet:
        return JsonResponse(
            {"error": "No pet found for this user."}, status=404)

    pet_image_url = ""
    if pet.type.base_image:
        pet_image_url = request.build_absolute_uri(pet.type.base_image.url)

    # get user points from the profile
    user_points = target_user.profile.points if hasattr(
        target_user, "profile") else 0

    data = {
        "user_points": user_points,
        "pet_name": pet.name,
        "pet_health": pet.health,
        "pet_image": pet_image_url,
    }
    return JsonResponse(data)
