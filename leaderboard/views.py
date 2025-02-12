from django.shortcuts import render
from pets.models import Pet


def leaderboard_view(request):
    pets = Pet.objects.order_by('-points')[:10]
    return render(request, 'leaderboard.html', {'pets': pets})

# Create your views here.
