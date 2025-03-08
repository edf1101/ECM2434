from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.

def petreal_home(request:HttpRequest) -> HttpResponse:
    """
    This function renders the home page for the petreal app.

    @param request: HttpRequest object
    @return: HttpResponse object
    """

    return render(request, 'petreal/petreal_home.html')