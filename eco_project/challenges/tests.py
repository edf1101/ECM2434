"""
This module is to test the challenges app.
Mocks are used extensively to simplify the tests and to avoid side effects.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import json
from datetime import timedelta
from unittest.mock import patch, MagicMock

from challenges.models import Streak, ChallengeSettings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

#pylint: disable=W0613,C0415,W0611

import challenges.signals

from users.models import Profile


User = get_user_model()


class ChallengesAPITests(TestCase):
    """
    This class tests the challenges API
    """

    def setUp(self) -> None:
        """
        This method runs before each test to set up the environment for the tests.

        @return: None
        """

        # Create a test user, create a profile for them, then log them in
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user, defaults={"points": 0, "latitude": 0.0, "longitude": 0.0}
        )
        self.client.login(username="testuser", password="testpass")

        # Make the challenge settings object and set the default settings:
        # 1 day interval, 2 points for a question, 1 point for reaching a
        # feature.
        self.challenge_settings = ChallengeSettings.get_solo()
        self.challenge_settings.interval = timedelta(days=1)
        self.challenge_settings.question_feature_points = 2
        self.challenge_settings.reached_feature_points = 1
        self.challenge_settings.save()

    def get_profile(self) -> Profile:
        """
        This gets an up to date version of the profile from the db

        @return: Profile
        """
        self.profile.refresh_from_db()
        return self.profile

    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_not_authenticated(
        self, mock_question_feature: MagicMock
    ) -> None:
        """
        Test that if a user is not authenticated, the API responds still with a correct/ incorrect
        message it just doesn't give points

        @param mock_question_feature: A mock of the QuestionFeature model
        @return: None
        """

        # Create a dummy question so we can control the behaviour of
        # is_valid_answer
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = True
        mock_question_feature.objects.get.return_value = dummy_question

        self.client.logout()  # make sure user is logged out
        data = {"answer": "dummy answer",
                "question_id": 1}  # create a dummy answer

        # call the api with the dummy answer
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # check that the response contains the correct message
        self.assertIn("but you are not signed in", response.data["message"])

    @patch("challenges.api.user_in_range_of_feature", return_value=False)
    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_out_of_range(
        self, mock_question_feature: MagicMock, mock_in_range: MagicMock
    ) -> None:
        """
        If the user is not in range of the feature, the API should respond appropriately.

        @param mock_question_feature: A mock of the QuestionFeature model
        @param mock_in_range: A mock of the user_in_range_of_feature function
        @return: None
        """

        # create the dummy question
        dummy_q_in_range = MagicMock()
        dummy_q_in_range.feature = MagicMock()
        dummy_q_in_range.is_valid_answer.return_value = True
        mock_question_feature.objects.get.return_value = dummy_q_in_range

        data = {"answer": "dummy answer in range", "question_id": 1}

        # mock call the api
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # assert that the response contains the correct message
        self.assertEqual(
            response.data["message"], "You are not in range of the feature"
        )

    @patch("challenges.api.user_already_reached_in_window", return_value=True)
    @patch("challenges.api.user_in_range_of_feature", return_value=True)
    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_already_reached(
        self,
        mock_question_feature: MagicMock,
        mock_in_range: MagicMock,
        mock_already_reached: MagicMock,
    ) -> None:
        """
        If the user has already reached the feature in the current window the api should respond
        with that in the message content

        @param mock_question_feature: A mock of the QuestionFeature model
        @param mock_in_range: A mock of the user_in_range_of_feature function
        @param mock_already_reached: A mock of the user_already_reached_in_window function
        @return: None
        """
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = True
        dummy_question.feature = MagicMock()
        mock_question_feature.objects.get.return_value = dummy_question

        data = {
            "answer": "dummy answer",
            "question_id": 1,
        }  # create the data to send to the api
        response = self.client.post(  # call the api
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(  # assert that the response states that the user has already reached it
            response.data["message"],
            "You have already reached this feature in this window",
        )

    @patch("challenges.api.user_already_reached_in_window", return_value=False)
    @patch("challenges.api.user_in_range_of_feature", return_value=True)
    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_correct_answer(
        self,
        mock_question_feature: MagicMock,
        mock_in_range: MagicMock,
        mock_already_reached: MagicMock,
    ) -> None:
        """
        This test asserts that a valid user in range who submits a correct answer is awarded points.

        @param mock_question_feature: A mock of the QuestionFeature model
        @param mock_in_range: A mock of the user_in_range_of_feature function
        @param mock_already_reached: A mock of the user_already_reached_in_window function
        @return: None
        """

        # create mock question
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = True
        dummy_question.feature = MagicMock()
        mock_question_feature.objects.get.return_value = dummy_question

        initial_points = (
            self.get_profile().points
        )  # get user initial points so we can check them
        data = {"answer": "correct answer", "question_id": 1}
        response = self.client.post(  # call the api
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertIn(
            "correct", response.data["message"]
        )  # check it was a correct answer

        profile = self.get_profile()
        self.assertEqual(  # Check that the user was awarded the correct number of points
            profile.points,
            initial_points + self.challenge_settings.question_feature_points,
        )

    @patch("challenges.api.user_already_reached_in_window", return_value=False)
    @patch("challenges.api.user_in_range_of_feature", return_value=True)
    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_incorrect_answer(
        self,
        mock_question_feature: MagicMock,
        mock_in_range: MagicMock,
        mock_already_reached: MagicMock,
    ) -> None:
        """
        This tests that a user who submits an incorrect answer does not receive points.

        @param mock_question_feature: A mock of the QuestionFeature model
        @param mock_in_range: A mock of the user_in_range_of_feature function
        @param mock_already_reached: A mock of the user_already_reached_in_window function
        @return: None
        """

        # create a dummy question
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = False
        dummy_question.feature = MagicMock()
        mock_question_feature.objects.get.return_value = dummy_question

        # create the data and post the request to the api
        data = {"answer": "wrong answer", "question_id": 1}
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # check that the response contains the correct message and no points
        # awarded
        self.assertIn("incorrect", response.data["message"])
        profile = self.get_profile()
        self.assertEqual(profile.points, 0)

    @patch("challenges.api.user_already_reached_in_window", return_value=False)
    @patch("challenges.api.haversine", return_value=1500)
    def test_nearest_challenges_api_authenticated(
        self, mock_haversine: MagicMock, mock_already_reached: MagicMock
    ) -> None:
        """
        For an authenticated user, nearest_challenges_api should return a list of nearby challenges

        @param mock_haversine: A mock of the haversine dist function
        @param mock_already_reached: A mock of the user_already_reached_in_window function
        """
        # locally import the FeatureType and FeatureInstance models to avoid
        # circular imports
        from locations.models import FeatureType, FeatureInstance

        # create a dummy feature and two instances of it so we can check the
        # closest one is first
        dummy_feature = FeatureType.objects.create(name="Dummy Feature")
        FeatureInstance.objects.create(
            feature=dummy_feature,
            latitude=0.1,
            longitude=0.1,
            name="Challenge 1",
            slug="challenge-1",
        )
        FeatureInstance.objects.create(
            feature=dummy_feature,
            latitude=0.2,
            longitude=0.2,
            name="Challenge 2",
            slug="challenge-2",
        )

        # call the api
        response = self.client.get(reverse("challenges:get_nearby_challenges"))

        # check that the response is correct
        self.assertEqual(response.status_code, 200)  # response exists?
        data = response.json()
        self.assertIn("challenges", data)
        self.assertLessEqual(len(data["challenges"]), 10)

        if data["challenges"]:  # check the data is OK
            self.assertIn("directions", data["challenges"][0])
            self.assertIn("description", data["challenges"][0])

    def test_nearest_challenges_api_not_authenticated(self) -> None:
        """
        For an unauthenticated user, nearest_challenges_api should return an empty list

        @return: None
        """

        self.client.logout()  # make sure the user is logged out

        # call the api and get response
        response = self.client.get(reverse("challenges:get_nearby_challenges"))

        # assert it is an empty list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["challenges"], [])

    def test_create_user_streak_signal(self) -> None:
        """
        Test that when a new user is created, a Streak object is also created with it using
        the signals.py module.

        @return: None
        """
        # create a new user
        new_user = User.objects.create_user(
            username="newuser", password="newpass")

        # profile should be made automatically but check it is there still
        Profile.objects.get_or_create(
            user=new_user,
            defaults={
                "points": 0,
                "latitude": 0.0,
                "longitude": 0.0})

        # assert streak created
        self.assertTrue(Streak.objects.filter(user=new_user).exists())
