"""
This module contains the API views for the users app.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def update_location(request) -> JsonResponse:
    """
    Update the logged-in user's profile with a new latitude and longitude.

    @param request: The request object.
    @return: The JSON response.
    """

    if not request.user.is_authenticated:  # handle non-signed in users
        return JsonResponse({'status': 'Not signed in'})

    lat = request.POST.get('lat')
    lon = request.POST.get('lon')

    if lat is None or lon is None:  # if there is no lat or lon
        return JsonResponse({'error': 'Missing latitude or longitude.'}, status=400)

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:  # if the lat or lon is not a number
        return JsonResponse({'error': 'Invalid coordinate values.'}, status=400)

    if not hasattr(request.user, 'profile'):  # if the user does not have a profile
        return JsonResponse({'error': 'User profile not found.'}, status=400)

    # actually set the data
    profile = request.user.profile
    profile.latitude = lat
    profile.longitude = lon
    profile.save()

    return JsonResponse({'status': 'success'})
