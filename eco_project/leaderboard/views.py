from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from pets.models import Pet
from users.models import UserGroup

User = get_user_model()


@login_required
def leaderboard_view(request) -> HttpResponse:
    """
    View to render the leaderboard page, showing the top users and pets.
    """
    top_users = User.objects.prefetch_related('pets').all()
    for user in top_users:
        user.total_pet_points = user.profile.points + sum(pet.points for pet in user.pets.all())

    pets = Pet.objects.order_by("-points")[:10]

    user_groups = UserGroup.objects.filter(users=request.user)

    selected_group = None
    group_users = []

    if user_groups.exists():
        group_code = request.GET.get("group")
        if group_code:
            selected_group = user_groups.filter(code=group_code).first()

    if selected_group:
        group_users = User.objects.filter(usergroup=selected_group).prefetch_related('pets')
        for user in group_users:
            user.total_pet_points = user.profile.points + sum(pet.points for pet in user.pets.all())

    context = {
        "users": top_users,
        "pets": pets,
        "user_groups": user_groups,
        "selected_group": selected_group,
        "group_users": group_users,
        "current_user": request.user,
    }

    return render(request, "leaderboard.html", context)
