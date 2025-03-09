"""
This module contains the views for the pets app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


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
def accessories(request) -> HttpResponse:
    """
    Display the accessories page for the logged in user's pet.
    Currently a placeholder for future accessory functionality with backend.
    """
    pet = request.user.pets.first()
    return render(request, "pets/accessories.html", {"pet": pet})
