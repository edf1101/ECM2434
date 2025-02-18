from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from users.models import Profile


@login_required
def view_pet(request) -> HttpResponse:
    profile: Profile = request.user.profile

    context = {
        "pet": profile.pet
    }

    return render(request, 'pets/mypet.html', context)
