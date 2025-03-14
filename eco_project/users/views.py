"""
This module contains the views for the users app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

from challenges.challenge_helpers import get_current_window
from challenges.models import UserFeatureReach, ChallengeSettings

from django.http.request import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .forms import ModifyUserForm, ModifyProfileForm, RegistrationForm
from .models import UserGroup

User = get_user_model()


def registration_view(request) -> HttpResponse:
    """
    This view is used to register a new user.

    @param request: The request object.
    @return: The response object.
    """

    # if the user is already logged in, redirect them to the homepage
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user, _ = form.save()
            login(request, user)
            return redirect("homepage")
    else:
        form = RegistrationForm()

    return render(request, "users/registration.html", {"form": form})


def login_view(request) -> HttpResponse:
    """
    Logs in a user. If the POST request comes from the homepage (via the hidden "next" field)
    and the login form is invalid, re-render the home_non_auth template so errors appear inline.
    Otherwise, render the standard login page.
    """
    if request.user.is_authenticated:
        return redirect("homepage")

    # find out next url if there is one
    next_url = request.POST.get("next") or request.GET.get("next", "")
    homepage_url = reverse("homepage")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url or homepage_url)

        # If the login was tried from the homepage go to the homepage
        if next_url == homepage_url:
            return render(request, "home.html", {"form": form})
        return render(request, "users/login.html",
                      {"form": form, "next": next_url})

    form = AuthenticationForm(request)
    return render(request, "users/login.html",
                  {"form": form, "next": next_url})


def logout_view(request) -> HttpResponse:
    """
    This view is used to log out a user then return them to the homepage.

    @param request: The request object.
    @return: The response object.
    """
    # if request.method == "POST":
    logout(request)
    return redirect("homepage")


def profile_view(request, username) -> HttpResponse:
    """
    This view is used to display a user's profile.

    @param request: The request object.
    @param username: The username of the user whose profile is being viewed.
    @return: The response object.
    """

    user = get_object_or_404(get_user_model(), username=username)

    # get all the badges the user has
    badge_instances = user.badgeinstance_set.all()
    badges = [badge_instance.badge for badge_instance in badge_instances]
    # sort the badges by their rarity so that the rarest ones are displayed first
    badges.sort(key=lambda badge: badge.rarity, reverse=True)
    # only show the first 5 badges
    badges = badges[:5]

    # Get the user's challenges completed in the current window
    now_time = timezone.now()
    interval = ChallengeSettings.get_solo().interval
    window_start, window_end = get_current_window(now_time, interval)
    user_feature_reaches = UserFeatureReach.objects.filter(
        user=user, reached_at__gte=window_start, reached_at__lt=window_end, extra="")
    # only take most recent 10
    user_feature_reaches = user_feature_reaches.order_by("-reached_at")[:10]

    pet = user.pets.first()  # assumes user only has one pet for sprint 1
    # if there is no pet fill this in with a default pet
    if not pet:
        pet = {
            "name": "Ellie the Elephant",
            "health": 100,
        }

    context = {
        "user": user,
        "badges": badges,
        "challenges": user_feature_reaches,
        "pet": pet,
    }
    return render(request, "users/profile.html", context=context)


@login_required
def edit_profile(request) -> HttpResponse:
    """
    Users who are logged in can edit their profile.

    @param request: The request object.
    @return: The response object.
    """

    user = request.user  # get the current user

    profile = user.profile  # get the profile

    if request.method == "POST":  # if we have just received a completed form
        user_form = ModifyUserForm(request.POST, instance=user)
        profile_form = ModifyProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect("users:user_profile", username=user.username)
    else:  # if we are just displaying the form for the first time
        user_form = ModifyUserForm(instance=user)
        profile_form = ModifyProfileForm(instance=profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "users/edit_profile.html", context)


@login_required
def change_password(request) -> HttpResponse:
    """
    Allow a logged-in user to change their password.

    @param request: The request object.
    @return: The response object.
    """

    if not request.user.is_authenticated:  # handle non-signed in users
        return redirect("users:login")

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # This saves the new password

            update_session_auth_hash(
                request, user
            )  # Prevents the user from being logged out
            return redirect("homepage")  # redirect home
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "users/change_password.html", {"form": form})


@login_required
def groups_home(request) -> HttpResponse:
    """
    This view is used to display the groups home page.
    It has a list of all the groups the user is a member of as a link to the group page.
    It also has a button to create a new group.

    @param request: The request object.
    @return: The response object.
    """

    user = request.user

    # get the UserGroups the user is a part of by their code
    user_groups = UserGroup.objects.all().filter(users=user)
    context = {"user_groups": user_groups}

    return render(request, "users/groups.html", context=context)


@login_required
def friends_view(request: HttpRequest) -> HttpResponse:
    """
    View to display a user's friends and search for new friends.

    @param request: The request object.
    @return: The response object.
    """
    profile = request.user.profile
    # Get current friends (the ManyToManyField on Profile)
    current_friends = profile.friends.all()

    query = request.GET.get('q', '')
    search_results = []
    if query:
        # Search users by username (excluding yourself)
        search_results = User.objects.filter(username__icontains=query).exclude(pk=request.user.pk)
        # Exclude users that are already friends
        search_results = search_results.exclude(
            pk__in=[friend.user.pk for friend in current_friends]
        )

    context = {
        'current_friends': current_friends,
        'search_results': search_results,
        'query': query,
    }
    return render(request, 'users/friends.html', context)


@login_required
def add_friend(request: HttpRequest, user_id: int) -> HttpResponse:
    """
    Add a user as a friend.

    @param request: The request object.
    @param user_id: The id of the user to add as a friend.
    @return: The response object.
    """

    friend_user = get_object_or_404(User, pk=user_id)  # Get the user to add as a friend
    if friend_user != request.user:
        request.user.profile.friends.add(friend_user.profile)
    return redirect('users:friends_view')


@login_required
def remove_friend(request: HttpRequest, user_id: int) -> HttpResponse:
    """
    Remove a user as a friend.

    @param request: The request object.
    @param user_id: The id of the user to remove as a friend.
    @return: The response object.
    """
    friend_user = get_object_or_404(User, pk=user_id)

    # Ensure that the user is not trying to remove themselves
    if friend_user != request.user:
        request.user.profile.friends.remove(friend_user.profile)
    return redirect('users:friends_view')
