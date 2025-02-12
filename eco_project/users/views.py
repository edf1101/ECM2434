"""
This module contains the views for the users app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserCreationFormWithNames


def registration_view(request):
    """
    This view is used to register a new user.
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


def login_view(request):
    """
    This view is used to log in a user.
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


def logout_view(request):
    """
    This view is used to log out a user then return them to the homepage.
    """
    if request.method == "POST":
        logout(request)
        return redirect("homepage")
