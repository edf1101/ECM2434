from django.shortcuts import render

def view_pet(request):
    # Simply render the template; no database queries needed for this default page.
    return render(request, 'pets/mypet.html')
