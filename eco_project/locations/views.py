"""
This module contains the views for the locations app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from challenges.challenge_helpers import user_reached_feature, user_in_range_of_feature, \
    get_features_near
from django.http import HttpResponse
from django.shortcuts import render
from .models import FeatureInstance, FeatureType, QuestionFeature, LocationsAppSettings


def base_locations(request) -> HttpResponse:
    """
    This function returns the homepage for the locations app.

    @param request: The request object that gets passed to the view.
    @return: An HTTP webpage to render to the user.
    """
    generic_features = FeatureType.objects.all()
    context = {"feature_type_list": generic_features}
    return render(request, "locations/location_home.html", context=context)


def individual_feature_page(request, slug) -> HttpResponse:
    """
    This function returns the page for a specific feature instance ie not a feature type.

    @param request: The request object that gets passed to the view.
    @param slug: The slug (unique url name) of the feature.
    @return: An HTTP webpage to render to the user.
    """
    feature_instance: FeatureInstance = FeatureInstance.objects.get(slug=slug)
    context = {"feature_instance": feature_instance}

    # get if feature has a question or not then return correct template
    # get question from feature
    question = None
    for question in QuestionFeature.objects.all():
        if question.feature == feature_instance.feature:
            question = question.question

    # if user signed in update points for reaching feature
    if request.user.is_authenticated:
        user_reached_feature(request.user, feature_instance)

    context["in_range"] = user_in_range_of_feature(request.user, feature_instance)

    if feature_instance.has_question:
        context["question"] = question
        return render(
            request,
            "locations/feature_instance_with_q.html",
            context)

    context["question"] = None
    return render(request, "locations/feature_instance.html", context)


def generic_feature_page(request, id_arg) -> HttpResponse:
    """
    This function returns the page for a generic feature type.
    Ie a generic Water fountain NOT a specific water fountain.

    @param request: The request object that gets passed to the view.
    @param id_arg: The id (PK) of the feature.
    @return: The HTTP webpage to render to the user.
    """
    feature_type: FeatureType = FeatureType.objects.get(id=id_arg)

    # Get nearby feature instances of this type to display on the page

    # get user location if logged in else get default locations
    lat = LocationsAppSettings.get_instance().default_lat
    lon = LocationsAppSettings.get_instance().default_lon
    if request.user.is_authenticated:
        lat = request.user.profile.latitude
        lon = request.user.profile.longitude

    nearby_feature_instances = list(get_features_near(lat, lon, specific_feature=feature_type))

    context = {"feature_type": feature_type, 'nearby_features': nearby_feature_instances}

    return render(request, "locations/feature_type.html", context)
