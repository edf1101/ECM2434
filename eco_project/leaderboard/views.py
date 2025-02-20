from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User
from users.models import Profile, UserGroup
from pets.models import Pet
from django.contrib.auth.decorators import login_required


@login_required
def leaderboard_view(request):
    top_users = User.objects.select_related('profile').order_by('-profile__points')[:10]
    pets = Pet.objects.order_by('-points')[:10]

    user_groups = UserGroup.objects.filter(users=request.user)
    selected_group = None
    group_users = []

    if user_groups.exists():
        group_code = request.GET.get('group')
        if group_code:
            selected_group = user_groups.filter(code=group_code).first()

        if not selected_group:
            selected_group = user_groups.first()


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