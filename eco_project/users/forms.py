"""
This module contains the forms for the users app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from pets.models import Pet, PetType
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

class PetCreationForm(forms.ModelForm):
    name = forms.CharField(max_length=30, required=True,
                           help_text="Required. Enter the name of your pet."
                           )

    type = forms.ModelChoiceField(
        queryset=PetType.objects.all(),
        empty_label="Select a Pet Type",
    )

    class Meta:
        """
        This class is used to define the fields that will be included in the form.
        """
        model = Pet
        fields = ("name", "type")

    def save(self, commit=True):
        """
        Saves the pet instance to the database.

        :param commit: Whether to commit the changes to the database.
        :return: The saved Pet instance.
        """
        pet = super().save(commit=False)
        if commit:
            pet.save()
        return pet


    def is_valid(self) -> bool:
        """
        This method is used to check if the form is valid.

        @return: True if the form is valid, False otherwise.
        """
        valid = super().is_valid()
        if not valid:
            return False

        # if name is empty then its invalid
        if not self.cleaned_data.get("name"):
            self.add_error("name", "This field is required.")
            return False

        # if type is empty then its invalid
        if not self.cleaned_data.get("type"):
            self.add_error("type", "This field is required.")
            return False

        return True


class RegistrationForm(forms.Form):
    """
    A form to register a new user along with their pet.
    """
    user_form = UserCreationFormWithNames()
    pet_form = PetCreationForm()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_form = UserCreationFormWithNames(*args, **kwargs)
        self.pet_form = PetCreationForm(*args, **kwargs)

    def is_valid(self) -> bool:
        """
        Checks if both the user form and the pet form are valid.

        :return: True if both forms are valid, False otherwise.
        """
        return self.user_form.is_valid() and self.pet_form.is_valid()

    def save(self, commit=True):
        """
        Saves the user and their pet to the database.
        """
        user = self.user_form.save(commit)

        # We have to assign the pet's owner before it can be saved
        pet = self.pet_form.save(commit=False)
        pet.owner = user
        pet = self.pet_form.save(commit)

        return user, pet


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
