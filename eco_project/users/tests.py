"""
This module contains tests for the users app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Profile, Badge, BadgeInstance, UserGroup, generate_unique_code

User = get_user_model()


class ProfileModelTests(TestCase):
    """
    Test the Profile model.
    """

    def setUp(self) -> None:
        """
        Create a user and profile for testing.
        This is run before each test method to set up the test environment.

        @return: None
        """
        # Create a user
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        # profile should be automatically created but if not it will be created
        # here
        self.profile, created = Profile.objects.get_or_create(
            user=self.user, defaults={"bio": "Test bio"}
        )
        if not created:
            self.profile.bio = "Test bio"
            self.profile.save()

    def test_profile_str(self) -> None:
        """
        This test asserts that the __str__ method of the Profile model returns the expected string.

        @return: None
        """
        self.assertEqual(str(self.profile), "testuser's Profile")


class BadgeModelTests(TestCase):
    """
    Test the Badge model.
    """

    def test_badge_str(self) -> None:
        """
        This test asserts that the __str__ method of the Badge model works correctly.
        """

        # create a test badge
        badge = Badge.objects.create(
            title="Test Badge",
            hover_text="test hover text",
            colour="#FFD700",
            rarity=5)

        # assert __str__ returns correctly
        self.assertEqual(str(badge), "Test Badge")


class BadgeInstanceModelTests(TestCase):
    """
    Tests for  the BadgeInstance model.
    """

    def setUp(self) -> None:
        """
        A badge and user need to be created before each test - do that here.

        @return: None
        """

        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.badge = Badge.objects.create(
            title="Test Badge",
            hover_text="test hover text",
            colour="#FFD700",
            rarity=5)

    def test_badge_instance_str(self) -> None:
        """
        Test the __str__ method of the BadgeInstance model.

        @return: None
        """

        # create an instance of the Badge type made in the setUp method
        badge_instance = BadgeInstance.objects.create(
            badge=self.badge, user=self.user)

        # check it returns the expected string
        self.assertEqual(str(badge_instance), "testuser - Test Badge")

    def test_unique_badge_instance(self) -> None:
        """
        Test that a BadgeInstance can only be created once for a given user and badge.

        @return: None
        """
        BadgeInstance.objects.create(
            badge=self.badge, user=self.user
        )  # create the first one

        # Check that creating the same pairing raises an exception
        with self.assertRaises(Exception):
            BadgeInstance.objects.create(badge=self.badge, user=self.user)


class UserGroupModelTests(TestCase):
    """
    Test the UserGroup model.
    """

    def setUp(self) -> None:
        """
        The setUp method is run before each test method to set up the test environment
        to test the groups an admin member is needed along with a normal member and group.

        @return: None
        """

        # create the objects
        self.admin_user = User.objects.create_user(
            username="admin", password="adminpassword"
        )
        self.member_user = User.objects.create_user(
            username="member", password="memberpassword"
        )
        self.group = UserGroup.objects.create(
            name="Test Group", group_admin=self.admin_user
        )

        # Add the admin to the group's users
        self.group.users.add(self.admin_user)

    def test_users_in_group(self) -> None:
        """
        Test that the users_in_group property returns a string of all users in the group.

        @return: None
        """
        self.group.users.add(self.member_user)
        expected = f"{self.admin_user.username}, {self.member_user.username}"
        self.assertEqual(self.group.users_in_group, expected)

    def test_add_user(self) -> None:
        """
        Test that the add_user method adds a user to the group.

        @return: None
        """
        self.group.add_user(self.member_user)
        self.assertIn(self.member_user, self.group.users.all())

    def test_remove_user(self) -> None:
        """
        Test that the remove_user method removes a user from the group.

        @return: None
        """
        self.group.add_user(self.member_user)
        self.group.remove_user(self.member_user)
        self.assertNotIn(self.member_user, self.group.users.all())

    def test_remove_admin_raises_error(self) -> None:
        """
        Test that trying to remove the admin from the group raises an error.
        """
        with self.assertRaises(Exception):
            self.group.remove_user(self.admin_user)


class GenerateUniqueCodeTests(TestCase):
    """
    This class just tests that the generate_unique_code function works as expected.
    It should return a string of 6 uppercase letters.
    """

    def test_generate_unique_code(self) -> None:
        """
        Test that the generate_unique_code function returns a string of 6 uppercase letters.

        @return: None
        """
        code = generate_unique_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isupper())
        self.assertTrue(code.isalpha())
