"""
This module contains the form for the Feature model. It is used so that we can have a colour
picker in the admin menu.
"""
from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import FeatureType, LocationsAppSettings


class FeatureForm(ModelForm):
    """
    This class is a form that enables use of a colour picker
    for the colour field in the Feature model.
    """

    class Meta:
        """
        This class is used to define the model and fields that the form will use.
        """
        fields = '__all__'
        model = FeatureType
        widgets = {
            'colour': TextInput(attrs={'type': 'color'}),
        }

class LocationsAppSettingsForm(ModelForm):
    """
    This class is a form that enables use of a colour picker
    for the colour field in the LocationsAppSettings model.
    """

    class Meta:
        """
        This class is used to define the model and fields that the form will use.
        """
        fields = '__all__'
        model = LocationsAppSettings
        widgets = {
            'world_colour': TextInput(attrs={'type': 'color'}),
        }