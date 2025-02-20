from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User
from users.models import Profile, UserGroup
from pets.models import Pet
from django.contrib.auth.decorators import login_required


@login_required
def leaderboard_view(request):
    """
    View to render the leaderboard page, showing the top users and pets.
    This view includes the logic to handle user group selection and
    displays the users and pets based on their points.

    If a user is part of one or more groups, they can select a group
    to view the leaderboard for that specific group.

    Context:
    - 'users': A list of the top 10 users sorted by their profile points.
    - 'pets': A list of the top 10 pets sorted by points.
    - 'user_groups': List of groups the current user belongs to.
    - 'selected_group': The group selected by the user (if any).
    - 'group_users': A list of users in the selected group, sorted by points.
    - 'current_user': The user making the request.
    """
    top_users = User.objects.select_related('profile').order_by('-profile__points')[:10]

    pets = Pet.objects.order_by('-points')[:10]

    user_groups = UserGroup.objects.filter(users=request.user)

    selected_group = None
    group_users = []

    if user_groups.exists():
        group_code = request.GET.get('group')
        if group_code:
            selected_group = user_groups.filter(code=group_code).first()

    if selected_group:
        group_users = User.objects.filter(
            usergroup=selected_group
        ).select_related('profile').order_by('-profile__points')

    context = {
        'users': top_users,
        'pets': pets,
        'user_groups': user_groups,
        'selected_group': selected_group,
        'group_users': group_users,
        'current_user': request.user
    }

    return render(request, 'leaderboard.html', context)
