"""
This page handles the API endpoints for the petReal app.
"""
import json

from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import JsonResponse, HttpResponse

from .models import ReactionType, UserPhotoReaction, UserPhoto


@login_required
def add_reaction(request: HttpRequest) -> HttpResponse:
    """
    Adds a reaction to a photo.

    @param request: The HTTP request.
    @return: The HTTP response.
    """

    if request.method == 'POST':  # Only allow POST requests.
        # Get the reaction and photo owner's username from the request body.
        data = json.loads(request.body)
        reaction = data.get('reaction')
        photo_user = data.get('photo_user')

        # Get the photo
        try:
            photo = UserPhoto.objects.get(user_id__username=photo_user)
        except UserPhoto.DoesNotExist:
            return JsonResponse({'error': 'Photo not found'}, status=404)

        # Get the reaction type
        try:
            reaction_type = ReactionType.objects.get(icon=reaction)
        except ReactionType.DoesNotExist:
            return JsonResponse({'error': 'Invalid reaction'}, status=400)

        # Check if the user has already reacted to the photo.
        reaction_obj = UserPhotoReaction.objects.filter(
            reactor=request.user,
            reacted_photo=photo
        ).first()

        if reaction_obj:  # Update the reaction if it exists.
            reaction_obj.reaction_type_id = reaction_type
            reaction_obj.save()
        else:  # Otherwise, create a new reaction.
            UserPhotoReaction.objects.create(
                reactor=request.user,
                reacted_photo=photo,
                reaction_type_id=reaction_type
            )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
