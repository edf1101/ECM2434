"""
This module contains the views for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from pets.models import Cosmetic


@login_required
def view_pet(request) -> HttpResponse:
    """
    View for displaying the pet details

    @param request: HttpRequest object
    @return: HttpResponse object
    """
    pet = request.user.pets.first()
    return render(request, "pets/mypet.html", {"pet": pet})


@login_required
def shop(request) -> HttpResponse:
    """
    View for the pet accessories shop

    @param request: HttpRequest object
    @return: HttpResponse object
    """
    profile = request.user.profile
    all_items = Cosmetic.objects.all()
    return render(request, "pets/shop.html", {"profile": profile, "items": all_items})


@login_required
def buy_cosmetic(request, cosmetic_id) -> HttpResponse:
    """
    Handle the purchase of a cosmetic item.
    """
    cosmetic = get_object_or_404(Cosmetic, id=cosmetic_id)
    profile = request.user.profile

    if cosmetic in profile.owned_accessories.all():
        messages.error(request, "You already own this cosmetic.")
        return redirect('pets:shop')

    if profile.pet_bucks < cosmetic.price:
        messages.error(request, "Not enough pet bucks.")
        return redirect('pets:shop')

    profile.pet_bucks -= cosmetic.price
    profile.owned_accessories.add(cosmetic)
    profile.save()

    messages.success(request, f"You have successfully purchased {cosmetic.name}.")
    return redirect('pets:shop')


@login_required
def accessories(request) -> HttpResponse:
    """
    Display the accessories page for the logged in user's pet.
    """
    pet = request.user.pets.first()
    return render(request, "pets/accessories.html", {"pet": pet})
