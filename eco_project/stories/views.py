"""
This module holds the views for the stories app.
"""
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import UserPhoto, UserPhotoReaction, ReactionType


@login_required
def stories_home(request: HttpRequest) -> HttpResponse:
    """
    Renders the stories home page with all the photos and reactions.

    @param request: The HTTP request.
    @return: The HTTP response.
    """
    now = timezone.now()
    photos = UserPhoto.objects.filter(expiration_date__gt=now)

    # get all the stories photos and their reactions
    friend_profiles = request.user.profile.friends.all()  # returns Profile queryset
    allowed_user_ids = [request.user.pk] + [friend.user.pk for friend in friend_profiles]

    # Filter photos so only those from allowed users (yourself + friends) are shown
    photos = UserPhoto.objects.filter(expiration_date__gt=now, user_id__in=allowed_user_ids)

    photos_data = []
    for photo in photos:
        reactions_qs = UserPhotoReaction.objects.filter(reacted_photo=photo)
        reaction_summary = {}
        for reaction in reactions_qs:
            icon = reaction.reaction_type_id.icon
            reaction_summary[icon] = reaction_summary.get(icon, 0) + 1

        photos_data.append({
            'user': photo.user_id.username,
            'photo_url': photo.photo.url if photo.photo else '',
            'reactions': reaction_summary,
        })

    # Get all available reaction types and their icons.
    reaction_types = ReactionType.objects.all()
    reaction_icons = [reaction.icon for reaction in reaction_types]

    # get if the user has already posted a photo
    user_has_photo = UserPhoto.objects.filter(user_id=request.user).exists()

    context = {'photos': photos_data, 'reaction_icons': reaction_icons, 'has_photo': user_has_photo}

    return render(request, 'stories/stories_home.html', context)
