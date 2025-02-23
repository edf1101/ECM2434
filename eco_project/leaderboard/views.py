"""
Views for the leaderboard app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
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
    This view includes the logic to handle user group selection and
    displays the users and pets based on their points.

    If a user is part of one or more groups, they can select a group
    to view the leaderboard for that specific group.

    @param request: HttpRequest object
    @return: HttpResponse object
    """
    top_users = User.objects.select_related(
        "profile").order_by("-profile__points")[:10]

    pets = Pet.objects.order_by("-points")[:10]

    user_groups = UserGroup.objects.filter(users=request.user)

    selected_group = None
    group_users = []

    if user_groups.exists():
        group_code = request.GET.get("group")
        if group_code:
            selected_group = user_groups.filter(code=group_code).first()

    if selected_group:
        group_users = (
            User.objects.filter(usergroup=selected_group)
            .select_related("profile")
            .order_by("-profile__points")
        )

    context = {
        "users": top_users,
        "pets": pets,
        "user_groups": user_groups,
        "selected_group": selected_group,
        "group_users": group_users,
        "current_user": request.user,
    }

    return render(request, "leaderboard.html", context)
