"""
Views for the leaderboard app.
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
    View to render the leaderboard page, showing the top users, pets, groups, and friends.
    """
    top_users = User.objects.prefetch_related('pets').all()
    # sort top_users by profile.points
    top_users = sorted(top_users, key=lambda user: user.profile.points, reverse=True)

    pets = Pet.objects.order_by("-health")[:10]

    user_groups = UserGroup.objects.filter(users=request.user)

    # Get all groups and calculate their total points
    all_groups = UserGroup.objects.all().prefetch_related('users', 'users__pets', 'users__profile')
    top_groups = []

    for group in all_groups:
        group_users = User.objects.filter(usergroup=group).prefetch_related('pets', 'profile')
        total_group_points = sum(user.profile.points for user in group_users)
        top_groups.append({
            'group': group,
            'total_points': total_group_points,
            'member_count': group_users.count()
        })

    # Sort groups by total points
    top_groups = sorted(top_groups, key=lambda g: g['total_points'], reverse=True)[:10]

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

    # Build the friend leaderboard: include yourself and your friends
    friend_profiles = request.user.profile.friends.all()
    # Convert friend profiles to User objects and add the current user
    friend_list = [request.user] + [friend.user for friend in friend_profiles]
    # Sort by profile.points (highest first)
    friend_leaderboard = sorted(friend_list, key=lambda u: u.profile.points, reverse=True)

    context = {
        "users": top_users,
        "pets": pets,
        "user_groups": user_groups,
        "group_leaderboards": group_leaderboards,
        "current_user": request.user,
        "top_groups": top_groups,
        "friend_leaderboard": friend_leaderboard,
    }

    return render(request, "leaderboard.html", context)
