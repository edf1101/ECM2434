"""
This module contains the forms for the users app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Profile, Badge, UserGroup
from django.forms import ModelForm
from django.forms.widgets import TextInput


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

    def is_valid(self) -> bool:
        """
        This method is used to check if the form is valid.

        @return: True if the form is valid, False otherwise.
        """

        valid = super().is_valid()
        if not valid:
            return valid

        # if first name is empty then its invalid
        if not self.cleaned_data["first_name"]:
            self.add_error("first_name", "This field is required.")
            return False

        return True


class ModifyUserForm(forms.ModelForm):
    """
    This form is used to modify the user's first and last names.
    It is used when a user wants to update their profile.
    """

    class Meta:
        """
        This class is used to define the fields that will be included in the form
        """
        model = get_user_model()
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
        }

    def is_valid(self) -> bool:
        """
        This method is used to check if the form is valid.

        @return: True if the form is valid, False otherwise.
        """
        valid = super().is_valid()
        if not valid:
            return valid

        # if first name is empty then its invalid
        if not self.cleaned_data["first_name"]:
            self.add_error("first_name", "This field is required.")
            return False

        return True


class ModifyProfileForm(forms.ModelForm):
    """
    This form is used to modify the user's bio it has to be separate from the ModifyUserForm
    since the bio is stored in a separate model.
    """

    class Meta:
        """
        This class is used to define the fields that will be included in the form.
        """
        model = Profile
        fields = ['bio']
        labels = {
            'bio': 'Bio',
        }


class BadgeAdminForm(ModelForm):
    """
    This class is a form that enables use of a colour picker
    for the colour field in the Badge model.
    """

    class Meta:
        """
        This class is used to define the model and fields that the form will use.
        """
        fields = '__all__'
        model = Badge
        widgets = {
            'colour': TextInput(attrs={'type': 'color'}),
        }


class UserGroupForm(forms.ModelForm):
    """
    Custom form for UserGroup to validate that the group admin is among the selected users.
    """

    class Meta:
        """
        This class is used to define the model and fields that the form will use.
        """
        model = UserGroup
        fields = '__all__'

    def clean(self) -> dict:
        """
        This method is used to validate the form data.
        """
        cleaned_data = super().clean()
        group_admin = cleaned_data.get('group_admin')
        users = cleaned_data.get('users')
        if group_admin and users:  # check of group_admin and users are not None
            if group_admin not in users:  # check if group_admin is among the selected users
                raise forms.ValidationError("Group admin must be a member of the group.")
        else:
            raise forms.ValidationError("There are either no users or no group admin.")
        return cleaned_data
