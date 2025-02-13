"""
This module contains the basic low level views for the mysite app.
"""
from django.shortcuts import render


def homepage(request):
    """
    Render a basic homepage.
    """
    return render(request, 'home.html')
