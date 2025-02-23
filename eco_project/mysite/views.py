from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


def homepage(request:HttpRequest) -> HttpResponse:
    """
    Renders the homepage with a login form in case the user is not authenticated.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    form = AuthenticationForm(request)
    return render(request, 'home.html', {'form': form})


def about(request:HttpRequest) -> HttpResponse:
    """
    Renders the about page.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    return render(request, 'about.html')


def contact(request:HttpRequest) -> HttpResponse:
    """
    Renders the contact page.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    return render(request, 'contact.html')


def faq(request:HttpRequest) -> HttpResponse:
    """
    Renders the faq page.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    return render(request, 'faq.html')

