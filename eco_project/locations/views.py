"""
This module contains the views for the locations app.
The views for the app so far are:
- base_locations
- individual_feature_page
- generic_feature_page
- generic_feature_list
"""
from django.shortcuts import render
from django.http import HttpResponse

from .models import IndividualFeature, Feature


def base_locations(request) -> HttpResponse:
    """
    This function returns the homepage for the locations app.

    :param request: The request object that gets passed to the view.
    :return: An HTTP webpage to render to the user.
    """
    return HttpResponse('Locations Homepage')


def individual_feature_page(request, slug) -> HttpResponse:
    """
    This function returns the page for a specific feature ie not a feature type.

    :param request: The request object that gets passed to the view.
    :param slug: The slug (unique url name) of the feature.
    :return: An HTTP webpage to render to the user.
    """
    individual_feature: IndividualFeature = IndividualFeature.objects.get(slug=slug)
    context = {'individual_feature': individual_feature}
    return render(request, 'locations/specific_feature.html', context)


def generic_feature_page(request, id_arg) -> HttpResponse:
    """
    This function returns the page for a generic feature type.
    Ie a generic Water fountain NOT a specific water fountain.

    :param request: The request object that gets passed to the view.
    :param id_arg: The id (PK) of the feature.
    :return: The HTTP webpage to render to the user.
    """
    generic_feature: Feature = Feature.objects.get(id=id_arg)
    context = {'generic_feature': generic_feature}
    return render(request, 'locations/generic_feature.html', context)


def generic_feature_list(request) -> HttpResponse:
    """
    This function returns a webpage that lists all the generic features with hyperlinks.

    :param request:  The request object that gets passed to the view.
    :return: An HTTP webpage to render to the user.
    """
    generic_features = Feature.objects.all()
    context = {'generic_features': generic_features}
    return render(request, 'locations/generic_feature_list.html', context)
