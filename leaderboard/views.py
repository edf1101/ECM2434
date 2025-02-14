from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User
from users.models import Profile
from pets.models import Pet

def leaderboard_view(request):
    # Get users ordered by their profile points
    top_users = User.objects.select_related('profile').order_by('-profile__points')[:10]
    pets = Pet.objects.order_by('-points')[:10]
    return render(request, 'leaderboard.html', {'users': top_users, 'pets': pets})
