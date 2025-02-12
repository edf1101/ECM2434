"""
This module contains the views for the users app.
"""
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserCreationFormWithNames, ModifyUserForm, ModifyProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse


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
        form = UserCreationFormWithNames(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("homepage")
    else:
        form = UserCreationFormWithNames()
    return render(request, "users/registration.html", {"form": form})


def login_view(request) -> HttpResponse:
    """
    This view is used to log in a user.

    @param request: The request object.
    @return: The response object.
    """

    # if the user is already logged in, redirect them to the homepage
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("homepage")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


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

    context = {'user': user, 'badges': badges}
    return render(request, "users/profile.html", context=context)


def edit_profile(request) -> HttpResponse:
    """
    Users who are logged in can edit their profile.

    @param request: The request object.
    @return: The response object.
    """

    if not request.user.is_authenticated:  # handle non signed in users
        return redirect("users:login")

    user = request.user  # get the current user

    profile = user.profile  # get the profile

    if request.method == 'POST':  # if we have just received a completed form
        user_form = ModifyUserForm(request.POST, instance=user)
        profile_form = ModifyProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect('users:user_profile', username=user.username)
    else:  # if we are just displaying the form for the first time
        user_form = ModifyUserForm(instance=user)
        profile_form = ModifyProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/edit_profile.html', context)


def change_password(request) -> HttpResponse:
    """
    Allow a logged-in user to change their password.

    @param request: The request object.
    @return: The response object.
    """

    if not request.user.is_authenticated:  # handle non-signed in users
        return redirect("users:login")

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # This saves the new password

            update_session_auth_hash(request, user)  # Prevents the user from being logged out
            return redirect('homepage')  # redirect home
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/change_password.html', {'form': form})
