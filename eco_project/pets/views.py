from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

@login_required
def view_pet(request) -> HttpResponse:
    """
    View for displaying the pet details

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    pet = request.user.pets.first()
    return render(request, 'pets/mypet.html', {'pet': pet})