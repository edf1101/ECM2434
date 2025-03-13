"""
This module contains the test suite for the leaderboard app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from pets.models import Pet, PetType
from users.models import Profile, UserGroup

User = get_user_model()


class LeaderboardViewTest(TestCase):
    """
    Test suite for the leaderboard view.
    Ensures that the leaderboard page functions correctly
    Tests included are: checking the behavior when the user is not logged in,
    when a group is selected, and when no group is selected.
    """

    def setUp(self) -> None:
        """
        Set up the test environment by creating necessary data, including users,
        profiles, pets, and groups. This will be executed before each test method.
        """
        self.client = Client()

        self.user1 = User.objects.create_user(
            username="user1", password="testpass")
        self.user2 = User.objects.create_user(
            username="user2", password="testpass")

        self.profile1, _ = Profile.objects.get_or_create(
            user=self.user1, defaults={"points": 50}
        )
        self.profile2, _ = Profile.objects.get_or_create(
            user=self.user2, defaults={"points": 100}
        )

        self.pet_type = PetType.objects.create(
            name="Dog", description="Test Dog")

        self.pet1 = Pet.objects.create(
            name="Pet1", type=self.pet_type, owner=self.user1
        )
        self.pet2 = Pet.objects.create(
            name="Pet2", type=self.pet_type, owner=self.user2
        )

        self.group = UserGroup.objects.create(name="Group1", code="G1")
        self.group.users.add(self.user1, self.user2)

    def test_redirect_if_not_logged_in(self) -> None:
        """
        Test that an unauthenticated user is redirected to the login page
        when trying to access the leaderboard.

        @return: None
        """
        response = self.client.get(reverse("leaderboard:leaderboard"))
        self.assertEqual(response.status_code, 302)

    def test_leaderboard_view_logged_in(self) -> None:
        """
        Test that the leaderboard view displays correctly for a logged-in user,
        including rendering the correct template and ensuring that the context
        contains the expected 'users' and 'pets' data sorted by points.

        @return: None
        """
        self.client.login(username="user1", password="testpass")
        response = self.client.get(reverse("leaderboard:leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leaderboard.html")
        self.assertIn("users", response.context)
        self.assertIn("pets", response.context)

        sorted_users = User.objects.select_related("profile").order_by(
            "-profile__points"
        )
        self.assertEqual(list(response.context["users"]), list(sorted_users))

        sorted_pets = Pet.objects.order_by("-health")
        self.assertEqual(list(response.context["pets"]), list(sorted_pets))

    # def test_leaderboard_with_group_selection(self) -> None:
    #     """
    #     Test that the leaderboard displays correctly when a specific user group
    #     is selected from the group dropdown. Verifies that the correct users
    #     from the selected group are displayed and sorted by points.
    #
    #     @return: None
    #     """
    #     self.client.login(username="user1", password="testpass")
    #     response = self.client.get(
    #         reverse("leaderboard:leaderboard"), {
    #             "group": "G1"})
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.context["selected_group"], self.group)
    #
    #     group_users = list(self.group.users.all())
    #
    #     self.assertIn(self.user1, group_users)
    #     self.assertIn(self.user2, group_users)
    #
    #     sorted_group_users = sorted(
    #         group_users, key=lambda u: u.profile.points, reverse=True
    #     )
    #     self.assertEqual(
    #         list(
    #             response.context["group_users"]),
    #         sorted_group_users)

    # def test_leaderboard_without_group_selection(self) -> None:
    #     """
    #     Test that the leaderboard displays correctly when no group is selected.
    #     Verifies that 'selected_group' is None and no group users are included
    #     in the context.
    #
    #     @return: None
    #     """
    #     self.client.login(username="user1", password="testpass")
    #     response = self.client.get(reverse("leaderboard:leaderboard"))
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNone(response.context["selected_group"])
    #     self.assertEqual(list(response.context["group_users"]), [])
