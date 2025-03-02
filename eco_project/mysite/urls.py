"""
This module contains the URL patterns for the project.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from django.views.static import serve

from . import views

urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/media/favicon.ico')),
    path("admin/", admin.site.urls),
    path("locations/", include("locations.urls")),
    path("users/", include("users.urls")),
    path("challenges/", include("challenges.urls")),
    path("pets/", include("pets.urls")),
    path("", views.homepage, name="homepage"),
    path("leaderboard/", include("leaderboard.urls")),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("gdpr/", views.gdpr, name="gdpr"),
]
