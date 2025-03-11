"""
This module contains the views for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from pets.models import Cosmetic, CosmeticType


@login_required
def view_pet(request) -> HttpResponse:
    """
    View for displaying the pet details

    @param request: HttpRequest object
    @return: HttpResponse object
    """

    pet = request.user.pets.first()
    return render(request, "pets/mypet.html", { "pet": pet })


@login_required
def shop(request) -> HttpResponse:
    """
    View for the pet accessories shop
    @param request: HttpRequest object
    @return: HttpResponse object
    """

    all_cosmetics = Cosmetic.objects.all()
    cosmetic_types = CosmeticType.objects.all()

    # Create dictionary of categories (including 'All') and the cosmetics in that category
    categories = [{ 'name': 'All', 'cosmetics': all_cosmetics }]
    categories += [
        { 'name': category.name, 'cosmetics': category.cosmetic_set.all() }
        for category in cosmetic_types
    ]

    return render(request, "pets/shop.html", {
        "profile": request.user.profile,
        "pet": request.user.pets.first(),
        "categories": categories,
    })

@login_required
def buy_cosmetic(request, cosmetic_id):
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

