"""
This module contains the API views for the users app.
"""
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import UserGroup


@require_POST
def update_location(request) -> JsonResponse:
    """
    Update the logged-in user's profile with a new latitude and longitude.

    @param request: The request object.
    @return: The JSON response.
    """

    if not request.user.is_authenticated:  # handle non-signed in users
        return JsonResponse({"status": "Not signed in"})

    lat = request.POST.get("lat")
    lon = request.POST.get("lon")

    if lat is None or lon is None:  # if there is no lat or lon
        return JsonResponse(
            {"error": "Missing latitude or longitude."}, status=400)

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:  # if the lat or lon is not a number
        return JsonResponse(
            {"error": "Invalid coordinate values."}, status=400)

    if not hasattr(
            request.user,
            "profile"):  # if the user does not have a profile
        return JsonResponse({"error": "User profile not found."}, status=400)

    # actually set the data
    profile = request.user.profile
    profile.latitude = lat
    profile.longitude = lon
    profile.save()

    return JsonResponse({"status": "success"})


@login_required
@require_POST
def create_group(request) -> JsonResponse:
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = {}
    group_name = data.get("name", "").strip()
    new_group = UserGroup.objects.create(
        group_admin=request.user, name=group_name)
    new_group.users.add(request.user)
    return JsonResponse({"code": new_group.code})


@login_required
@require_POST
def delete_group(request, code) -> JsonResponse:
    """
    API endpoint to delete a group.
    Only the group admin can delete the group.

    :param request: the request object
    :param code: the group code
    :return : the JSON response
    """
    group = get_object_or_404(UserGroup, code=code)

    if (
        request.user != group.group_admin
    ):  # if the user is not the admin return an error
        return JsonResponse({"error": "Permission denied."}, status=403)

    group.delete()
    return JsonResponse({"success": True})


@login_required
@require_POST
def remove_user_from_group(request, code) -> JsonResponse:
    """
    API endpoint to remove a user from a group (only group admin can do this).

    :param request: the request object
    :param code: the group code
    :return : the JSON response
    """

    group = get_object_or_404(UserGroup, code=code)  # get the group

    if (
        request.user != group.group_admin
    ):  # if the user is not the admin return an error
        return JsonResponse(
            {"error": "Permission denied."}, status=403
        )  # 403 is no perms

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    user_id = data.get("user_id")
    if not user_id:
        return JsonResponse({"error": "User id not provided."}, status=400)

    user_to_remove = get_object_or_404(User, pk=user_id)

    # Prevent the admin from removing themselves.
    if user_to_remove == group.group_admin:
        return JsonResponse(
            {"error": "Cannot remove the group admin."}, status=400)

    group.users.remove(user_to_remove)
    return JsonResponse({"success": True})


@login_required
@require_POST
def join_group(request) -> JsonResponse:
    """
    API endpoint for a user to join an existing group using a group code

    :param request: the request object
    :return : the JSON response
    """
    try:  # Try to parse the JSON data else return an error
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."}, status=400
        )  # 400 is bad request

    group_code = data.get("group_code")
    if not group_code:  # If there is no group code, return an error
        return JsonResponse({"error": "No group code provided."}, status=400)

    try:  # Try to get the group with the given code else return an error
        group = UserGroup.objects.get(code=group_code)
    except UserGroup.DoesNotExist:
        return JsonResponse(
            {"error": "Group does not exist."}, status=404
        )  # 404 is not found

    if (
        request.user in group.users.all()
    ):  # If the user is already in the group, return an error
        return JsonResponse(
            {"error": "You are already a member of this group."}, status=400
        )

    # If all else works then add the user to the group and return the group
    # code
    group.users.add(request.user)
    return JsonResponse({"success": True, "code": group.code})


@login_required
@require_POST
def leave_group(request, code) -> JsonResponse:
    """
    API endpoint for a user to leave a group

    :param request: the request object
    :param code: the group code
    :return   : the JSON response
    """
    group = get_object_or_404(UserGroup, code=code)

    # If the user is the admin, do not allow leaving.
    if request.user == group.group_admin:
        return JsonResponse(
            {"error": "Group admin cannot leave the group, only delete the group."},
            status=400,
        )

    group.users.remove(request.user)
    return JsonResponse({"success": True})
