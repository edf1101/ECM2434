"""
This module contains the views for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404, redirect

from pets.models import Cosmetic, CosmeticType, Pet


@login_required
def view_pet(request) -> HttpResponse:
    """
    View for displaying the pet details.

    @param request: HttpRequest object
    @return: HttpResponse object
    """

    return render(request, "pets/mypet.html", {
        "pet": request.user.pets.first(),
        "profile": request.user.profile
    })

@login_required
def equip_cosmetic(request, cosmetic_id: int, equip: int) -> HttpResponse:
    """
    Handle the equipping (if `equip=1`) or removal (if `equip=0`) of a cosmetic.

    @param request: HttpRequest object
    @param cosmetic_id: The ID of the cosmetic
    @param equip: Whether to equip (1) or remove (0) the cosmetic
    @return: Redirect to mypet page
    """

    cosmetic = get_object_or_404(Cosmetic, id=cosmetic_id)
    profile = request.user.profile
    pet: Pet = request.user.pets.first()

    if cosmetic not in profile.owned_accessories.all():
        messages.error(request, "You do not own this cosmetic.")
        return redirect('pets:mypet')

    if equip:
        if cosmetic in pet.cosmetics.all():
            messages.info(request, "This cosmetic is already equipped.")
        else:
            cosmetic_type: CosmeticType = cosmetic.type

            # Remove all other cosmetics of the same type (a pet can only wear one hat, etc.)
            for other in pet.cosmetics.all():
                if other.type == cosmetic_type:
                    pet.cosmetics.remove(other)

            pet.cosmetics.add(cosmetic)
            messages.success(request, f"{cosmetic.name} has been equipped.")
    else:
        if cosmetic in pet.cosmetics.all():
            pet.cosmetics.remove(cosmetic)
            messages.success(request, f"{cosmetic.name} has been removed.")
        else:
            messages.info(request, "This cosmetic is not equipped.")

    pet.save()

    return redirect('pets:mypet')


@login_required
def shop(request) -> HttpResponse:
    """
    View for the pet accessories shop.

    @param request: HttpRequest object
    @return: HttpResponse object
    """

    all_cosmetics = Cosmetic.objects.all()
    cosmetic_types = CosmeticType.objects.all()

    # Create dictionary of categories (including 'All') and the cosmetics in that category
    categories = [{'name': 'All', 'cosmetics': all_cosmetics}]
    categories += [
        {'name': category.name, 'cosmetics': category.cosmetic_set.all()}
        for category in cosmetic_types
    ]

    return render(request, "pets/shop.html", {
        "profile": request.user.profile,
        "pet": request.user.pets.first(),
        "categories": categories,
    })


@login_required
def buy_cosmetic(request, cosmetic_id: int):
    """
    Requests to buy cosmetic with ID `cosmetic_id`.

    @param request: HttpRequest object
    @param cosmetic_id: The ID of the cosmetic to buy
    @return: Redirects to shop
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
