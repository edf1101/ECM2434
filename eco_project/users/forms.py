"""
This module contains the forms for the users app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserCreationFormWithNames(UserCreationForm):
    """
    This form is used to register a new user, it includes required fields for first name
     and last name.
    """
    first_name = forms.CharField(max_length=30, required=True,
                                 help_text="Required. Enter your first name."
                                 )
    last_name = forms.CharField(max_length=30, required=True,
                                help_text="Required. Enter your last name."
                                )

    class Meta(UserCreationForm.Meta):
        """
        This class is used to define the fields that will be included in the form.
        """
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        """
        This method is used to save the user to the database.
        """
        user = super().save(commit=False)

        # these aren't done by default so set them
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
