"""
This page handles the API endpoints for the stories app.
"""
import base64
import json
import uuid
from datetime import timedelta

from django.core.files.base import ContentFile
from django.utils import timezone

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


@login_required
def add_pet_real(request: HttpRequest) -> HttpResponse:
    """
    Adds a story photo.

    @param request: The HTTP request.
    @return: The HTTP response.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        photo_data = data.get('photo')

        # Decode the received photo
        if photo_data and ';base64,' in photo_data:
            header, img_str = photo_data.split(';base64,')

            ext = header.split('/')[-1]  # Get the file extension
            photo_file = ContentFile(base64.b64decode(img_str), name=f"{uuid.uuid4()}.{ext}")
        else:
            return JsonResponse({'error': 'Invalid image data'}, status=400)

        # Set exp date for photo
        expiration_date = timezone.now() + timedelta(days=1)

        # Create object
        UserPhoto.objects.create(
            user_id=request.user,
            photo=photo_file,
            expiration_date=expiration_date
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)  # error
