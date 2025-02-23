from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def homepage(request:HttpRequest) -> HttpResponse:
    """
    Renders the homepage with a login form in case the user is not authenticated.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    form = AuthenticationForm(request)
    return render(request, 'home.html', {'form': form})
