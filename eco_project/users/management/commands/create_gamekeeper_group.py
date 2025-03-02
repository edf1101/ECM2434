"""
This module is used to run a command 'create roles' that sets up a gamekeeper group
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    """
    This command creates the gamekeepers group
    """
    help = 'Creates the "gamekeepers" user group with predefined permissions'

    def handle(self, *args, **kwargs) -> None:
        """
        Create the roles required

        @return: None
        """
        self.create_gamekeepers_role()

    def create_gamekeepers_role(self) -> None:
        """
        This function is used to setup the gamekeepers group

        @return: None
        """
        # Hardcoded list of permissions
        permissions_list = [
            # Users | Badge
            ("users", "badge", "add_badge"),
            ("users", "badge", "change_badge"),
            ("users", "badge", "delete_badge"),
            ("users", "badge", "view_badge"),

            # Users | Badge Instance
            ("users", "badgeinstance", "add_badgeinstance"),
            ("users", "badgeinstance", "change_badgeinstance"),
            ("users", "badgeinstance", "delete_badgeinstance"),
            ("users", "badgeinstance", "view_badgeinstance"),

            # Users | Profile
            ("users", "profile", "change_profile"),
            ("users", "profile", "view_profile"),

            # Users | User Group
            ("users", "usergroup", "add_usergroup"),
            ("users", "usergroup", "change_usergroup"),
            ("users", "usergroup", "delete_usergroup"),
            ("users", "usergroup", "view_usergroup"),

            # Pets | Pet
            ("pets", "pet", "add_pet"),
            ("pets", "pet", "change_pet"),
            ("pets", "pet", "delete_pet"),
            ("pets", "pet", "view_pet"),

            # Pets | Pet Type
            ("pets", "pettype", "add_pettype"),
            ("pets", "pettype", "change_pettype"),
            ("pets", "pettype", "delete_pettype"),
            ("pets", "pettype", "view_pettype"),

            # Pets | Cosmetic
            ("pets", "cosmetic", "add_cosmetic"),
            ("pets", "cosmetic", "change_cosmetic"),
            ("pets", "cosmetic", "delete_cosmetic"),
            ("pets", "cosmetic", "view_cosmetic"),

            # Pets | Cosmetic Type
            ("pets", "cosmetictype", "add_cosmetictype"),
            ("pets", "cosmetictype", "change_cosmetictype"),
            ("pets", "cosmetictype", "delete_cosmetictype"),
            ("pets", "cosmetictype", "view_cosmetictype"),

            # Locations | Feature Type
            ("locations", "featuretype", "add_featuretype"),
            ("locations", "featuretype", "change_featuretype"),
            ("locations", "featuretype", "delete_featuretype"),
            ("locations", "featuretype", "view_featuretype"),

            # Locations | Question Answer
            ("locations", "questionanswer", "add_questionanswer"),
            ("locations", "questionanswer", "change_questionanswer"),
            ("locations", "questionanswer", "delete_questionanswer"),
            ("locations", "questionanswer", "view_questionanswer"),

            # Locations | Question Feature
            ("locations", "questionfeature", "add_questionfeature"),
            ("locations", "questionfeature", "change_questionfeature"),
            ("locations", "questionfeature", "delete_questionfeature"),
            ("locations", "questionfeature", "view_questionfeature"),

            # Locations | Feature Instance
            ("locations", "featureinstance", "add_featureinstance"),
            ("locations", "featureinstance", "change_featureinstance"),
            ("locations", "featureinstance", "delete_featureinstance"),
            ("locations", "featureinstance", "view_featureinstance"),

            # Administration | Log Entry
            ("admin", "logentry", "view_logentry"),

            # Authentication and Authorization | User
            ("auth", "user", "add_user"),
            ("auth", "user", "change_user"),
            ("auth", "user", "delete_user"),
            ("auth", "user", "view_user"),

            # Challenges | Challenge Settings
            ("challenges", "challengesettings", "change_challengesettings"),
            ("challenges", "challengesettings", "view_challengesettings"),

            # Challenges | Streak
            ("challenges", "streak", "change_streak"),
            ("challenges", "streak", "view_streak"),
        ]

        # Delete existing group if it exists
        try:
            existing_group = Group.objects.get(name='Gamekeepers')
            existing_group.delete()
        except Group.DoesNotExist:
            pass
        # Create the new group
        group = Group.objects.create(name='Gamekeepers')
        # Add hardcoded permissions to the group
        for app_label, model_name, codename in permissions_list:
            try:
                permission = Permission.objects.get(
                    content_type__app_label=app_label,
                    content_type__model=model_name,
                    codename=codename
                )
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'Permission "{codename}" for model "{model_name}" '
                    f'in app "{app_label}" not found.'
                ))
        group.save()
        # Check that the number of permissions is correct
        total_permissions = group.permissions.count()
        expected_permissions = len(permissions_list)

        if total_permissions == expected_permissions:
            self.stdout.write(self.style.SUCCESS(
                'Successfully created group Gamekeepers".'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f'Error: Group "Gamekeepers" has {total_permissions} permissions, but '
                f'{expected_permissions} were expected.'
            ))
