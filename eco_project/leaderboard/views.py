"""
Views for the leaderboard app.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from pets.models import Pet
from users.models import UserGroup

from django.views.generic import DetailView

User = get_user_model()


@login_required
def leaderboard_view(request) -> HttpResponse:
    """
    View to render the leaderboard page, showing the top users and pets.
    """
    top_users = User.objects.prefetch_related('pets').all()
    # sort top_users by profile.points
    top_users = sorted(top_users, key=lambda user: user.profile.points, reverse=True)

    pets = Pet.objects.order_by("-health")[:10]

    user_groups = UserGroup.objects.filter(users=request.user)


    group_leaderboards = []
    for group in user_groups:
        group_users = User.objects.filter(usergroup=group).prefetch_related('pets')
        for user in group_users:
            user.total_pet_points = user.profile.points + sum(pet.points for pet in user.pets.all())
        sorted_users = sorted(group_users, key=lambda u: u.total_pet_points, reverse=True)
        group_leaderboards.append({
            'group': group,
            'users': sorted_users,
        })

    context = {
        "users": top_users,
        "pets": pets,
        "user_groups": user_groups,
        "group_leaderboards": group_leaderboards,
        "current_user": request.user,
    }

    return render(request, "leaderboard.html", context)
