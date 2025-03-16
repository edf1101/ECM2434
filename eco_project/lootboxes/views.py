from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LootBox

@login_required
def spin_lootbox(request):
    try:
        lootbox = request.user.lootbox
    except LootBox.DoesNotExist:
        lootbox = LootBox.objects.create(user=request.user)  # Initialize LootBox for user if not exists

    if request.method == "POST":
        try:
            result = lootbox.spin()  # Spin the lootbox wheel and update points
            messages.success(request, result)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "lootboxes/spin.html", {"lootbox": lootbox, "profile": request.user.profile})
