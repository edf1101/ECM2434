from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required
def view_pet(request) -> HttpResponse:
    """
    View for displaying the pet details

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    pet = request.user.pets.first()
    return render(request, 'pets/mypet.html', {'pet': pet})