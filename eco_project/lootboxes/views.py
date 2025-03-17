from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LootBox
from django.http import JsonResponse


#@login_required
#def spin_lootbox(request):
#    try:
#        lootbox = request.user.lootbox
#    except LootBox.DoesNotExist:
#        lootbox = LootBox.objects.create(user=request.user)  # Initialize LootBox for user if not exists

#    if request.method == "POST":
#        try:
#            result = lootbox.spin()  # Spin the lootbox wheel and update points
#            messages.success(request, result)
#        except ValueError as e:
#            messages.error(request, str(e))

#    return render(request, "lootboxes/spin.html", {"lootbox": lootbox, "profile": request.user.profile})

def spin_lootbox(request):
    profile = request.user.profile
    if request.method == "POST":
        try:
            # Access the user's lootbox instance
            lootbox = request.user.lootbox
            result = lootbox.spin()  # Call the spin method to perform the spin logic
            return JsonResponse({'result': result})
        except ValueError as e:
<<<<<<< HEAD
            # In case of an error (e.g., not enough bucks), send the error as a response
            # messages.error(request, str(e))
            return JsonResponse({'result': str(e)}, status=400)
    return render(request, 'lootboxes/spin.html', {
        'profile': profile,
    })
=======
            messages.error(request, str(e))

    return render(request, "lootboxes/spin.html", {"lootbox": lootbox, "profile": request.user.profile})

@login_required
def spin_view(request):
    return render(request, "spinningwheel/spin.html")
>>>>>>> 2559cb5 (Wheel creation)
