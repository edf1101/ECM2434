"""
This module is used to run a command 'create_demo_users' that sets up a gamekeeper and an admin
"""
import sys

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from pets.models import Pet, PetType  # Import your Pet models here if not already imported

User = get_user_model()


class Command(BaseCommand):
    """
    This command creates the demo users for the gamekeeper and admin
    """
    help = 'Creates the demo users for the gamekeeper and admin roles'

    def handle(self, *args, **kwargs) -> None:
        """
        Create the roles required

        @return: None
        """
        self.create_users()

    def create_users(self) -> None:
        """
        Try to create demo admin and gamekeeper users

        @return: None
        """

        # Try to get the 'gamekeepers' group
        try:
            gamekeepers_group = Group.objects.get(name='Gamekeepers')
        except Group.DoesNotExist:
            gamekeepers_group = None
            self.stdout.write(self.style.ERROR("Gamekeeper group does't exist"))
            sys.exit()

        # 1. Create admin superuser
        try:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.ERROR("Error making admin demo user (already exists)"))
            sys.exit()
        except User.DoesNotExist:
            try:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    password='admin',
                    is_staff=True
                )
            except IntegrityError as _:
                self.stdout.write(self.style.ERROR("Error making admin demo user"))
                sys.exit()

        # 2. Create gamekeeper user
        try:
            gamekeeper_user = User.objects.get(username='gamekeeper')
            self.stdout.write(
                self.style.ERROR("Error making gamekeeper demo user (already exists)"))
            sys.exit()
        except User.DoesNotExist:
            try:
                gamekeeper_user = User.objects.create_user(
                    username='gamekeeper',
                    password='gamekeeper',
                    is_staff=True
                )
                if gamekeepers_group:
                    gamekeeper_user.groups.add(gamekeepers_group)
            except IntegrityError as _:
                self.stdout.write(self.style.ERROR("Error making gamekeeper demo user"))
                sys.exit()

        if len(PetType.objects.all()) == 0:  # get a default pet if there is one
            self.stdout.write(self.style.ERROR("No default pet available"))
            sys.exit()
        default_pettype = PetType.objects.all()[0]

        # Helper function to ensure a user has at least one pet
        def ensure_user_has_pet(user_obj, pet_name):
            if not user_obj or not default_pettype:
                return
            # Check if the user already has any pets
            existing_pet = Pet.objects.filter(owner=user_obj).first()
            if existing_pet:
                self.stdout.write(self.style.ERROR("Error making gamekeeper demo user's pet"))
                sys.exit()
            else:
                try:
                    Pet.objects.create(
                        name=pet_name,
                        type=default_pettype,
                        owner=user_obj,
                        health=100,
                    )
                except IntegrityError as _:
                    self.stdout.write(self.style.ERROR("Error making gamekeeper demo user's pet"))
                    sys.exit()

        # Create pets if the users were successfully created
        ensure_user_has_pet(admin_user, "Admin's Pet")

        ensure_user_has_pet(gamekeeper_user, "Gamekeeper's Pet")

        self.stdout.write(self.style.SUCCESS(
            'Successfully created demo users'
        ))
