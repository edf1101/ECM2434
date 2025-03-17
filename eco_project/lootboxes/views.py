"""
This module contains the views for the lootboxes app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LootBox


@login_required
def spin_lootbox(request):
    """
    This function handles the spinning of the lootbox wheel.

    :param request: The request object.
    :return: A response object.
    """
    try:
        lootbox = request.user.lootbox
    except LootBox.DoesNotExist:
        # Initialize LootBox for user if not exists
        lootbox = LootBox.objects.create(user=request.user)

    if request.method == "POST":
        try:
            result = lootbox.spin()  # Spin the lootbox wheel and update points
            messages.success(request, result)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, "lootboxes/spin.html",
                  {"lootbox": lootbox, "profile": request.user.profile})
