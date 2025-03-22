"""
This module contains tests for the challenges app.
Mocks are utilized extensively to simplify the tests and avoid side effects from interacting with external services or databases.

Authors: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

import json
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.utils import timezone

from challenges.models import Streak, UserFeatureReach, ChallengeSettings, get_current_window, Quiz, QuizAttempt, Question, Choice
from challenges.apps import ChallengesConfig
from challenges.tasks import reset_missed_streaks, cleanup_user_feature_reaches, update_pet_health, update_challenges
from django.contrib.auth import get_user_model
from locations.models import LocationsAppSettings
from django.test import TestCase
from django.urls import reverse
from pets.models import Pet, PetType


# Pylint error suppression for specific cases
# pylint: disable=W0613,C0415,W0611

import challenges.signals

from users.models import Profile

User = get_user_model()


class ChallengesAPITests(TestCase):
    """
    This class contains tests for the challenges API endpoints.
    """

    def setUp(self) -> None:
        """
        Sets up the test environment before each test.
        Creates a test user, logs them in, and sets default challenge settings.

        @return: None
        """
        # Create a test user and profile, then log in
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user, defaults={"points": 0, "latitude": 0.0, "longitude": 0.0}
        )
        self.client.login(username="testuser", password="testpass")

        # Set up the default challenge settings
        self.challenge_settings = ChallengeSettings.get_solo()
        self.challenge_settings.interval = timedelta(days=1)
        self.challenge_settings.question_feature_points = 2
        self.challenge_settings.reached_feature_points = 1
        self.challenge_settings.save()

    def get_profile(self) -> Profile:
        """
        Retrieves the latest version of the profile from the database.

        @return: Profile object
        """
        self.profile.refresh_from_db()
        return self.profile

    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_not_authenticated(
        self, mock_question_feature: MagicMock
    ) -> None:
        """
        Tests the API response when the user is not authenticated.
        Verifies that the response correctly informs the user but does not award points.

        @param mock_question_feature: Mock of the QuestionFeature model
        @return: None
        """

        # Mock a dummy question
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = True
        mock_question_feature.objects.get.return_value = dummy_question

        self.client.logout()  # Ensure user is logged out
        data = {"answer": "dummy answer", "question_id": 1}  # Dummy answer data

        # Make API call with dummy answer data
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains a message about the user not being signed in
        self.assertIn("but you are not signed in", response.data["message"])

    @patch("challenges.api.user_in_range_of_feature", return_value=False)
    @patch("challenges.api.QuestionFeature")
    def test_submit_answer_api_out_of_range(
        self, mock_question_feature: MagicMock, mock_in_range: MagicMock
    ) -> None:
        """
        Tests the API response when the user is out of range of the feature.
        Verifies the response appropriately informs the user.

        @param mock_question_feature: Mock of the QuestionFeature model
        @param mock_in_range: Mock of the user_in_range_of_feature function
        @return: None
        """

        # Mock question with feature and validity
        dummy_q_in_range = MagicMock()
        dummy_q_in_range.feature = MagicMock()
        dummy_q_in_range.is_valid_answer.return_value = True
        mock_question_feature.objects.get.return_value = dummy_q_in_range

        data = {"answer": "dummy answer in range", "question_id": 1}

        # Call API
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # Verify that the response indicates the user is out of range
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
        Tests the API response when the user has already reached the feature in the current window.
        Verifies that the correct message is returned to the user.

        @param mock_question_feature: Mock of the QuestionFeature model
        @param mock_in_range: Mock of the user_in_range_of_feature function
        @param mock_already_reached: Mock of the user_already_reached_in_window function
        @return: None
        """
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = True
        dummy_question.feature = MagicMock()
        mock_question_feature.objects.get.return_value = dummy_question

        data = {"answer": "dummy answer", "question_id": 1}  # Dummy data for API call

        # Call API
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # Verify that the response states the feature has already been reached
        self.assertEqual(
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
        Tests the API response for a correct answer submission by an authenticated user.
        Verifies that the user is awarded points.

        @param mock_question_feature: Mock of the QuestionFeature model
        @param mock_in_range: Mock of the user_in_range_of_feature function
        @param mock_already_reached: Mock of the user_already_reached_in_window function
        @return: None
        """

        # Create a mock question with a valid answer
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = True
        dummy_question.feature = MagicMock()
        mock_question_feature.objects.get.return_value = dummy_question

        initial_points = self.get_profile().points  # Get initial points to verify increase

        # Data for correct answer submission
        data = {"answer": "correct answer", "question_id": 1}

        # Call API to submit the correct answer
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # Verify the response message indicates a correct answer
        self.assertIn("correct", response.data["message"])

        profile = self.get_profile()
        # Assert the user points increased correctly
        self.assertEqual(
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
        Tests the API response for an incorrect answer submission.
        Verifies that no points are awarded.

        @param mock_question_feature: Mock of the QuestionFeature model
        @param mock_in_range: Mock of the user_in_range_of_feature function
        @param mock_already_reached: Mock of the user_already_reached_in_window function
        @return: None
        """

        # Mock a question with an invalid answer
        dummy_question = MagicMock()
        dummy_question.is_valid_answer.return_value = False
        dummy_question.feature = MagicMock()
        mock_question_feature.objects.get.return_value = dummy_question

        # Data for incorrect answer submission
        data = {"answer": "wrong answer", "question_id": 1}

        # Call API to submit the incorrect answer
        response = self.client.post(
            reverse("challenges:submit_answer_api"),
            data=json.dumps(data),
            content_type="application/json",
        )

        # Verify the response message indicates an incorrect answer and no points awarded
        self.assertIn("incorrect", response.data["message"])
        profile = self.get_profile()
        self.assertEqual(profile.points, 0)

    @patch("challenges.api.user_already_reached_in_window", return_value=False)
    @patch("challenges.challenge_helpers.haversine", return_value=1500)
    def test_nearest_challenges_api_authenticated(
        self, mock_haversine: MagicMock, mock_already_reached: MagicMock
    ) -> None:
        """
        Verifies the nearest challenges API for an authenticated user returns nearby challenges.

        @param mock_haversine: Mock of the haversine distance function
        @param mock_already_reached: Mock of the user_already_reached_in_window function
        @return: None
        """
        # Locally import necessary models to avoid circular imports
        from locations.models import FeatureType, FeatureInstance

        # Create dummy features and feature instances for the challenge
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

        # Call the API
        response = self.client.get(reverse("challenges:get_nearby_challenges"))

        # Assert the API response contains a list of challenges
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("challenges", data)
        self.assertLessEqual(len(data["challenges"]), 10)

        # Verify challenge data
        if data["challenges"]:
            self.assertIn("directions", data["challenges"][0])
            self.assertIn("description", data["challenges"][0])

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

        @patch('challenges.apps.scheduler')
        @patch('challenges.apps.atexit.register')
        def test_challenges_app_ready(self, mock_atexit_register, mock_scheduler):
            # Simulate that the app is ready (i.e., when the app starts)
            app_config = ChallengesConfig()

            # Call the ready method which should schedule the jobs
            app_config.ready()

            # Test if the scheduler's add_job method was called twice (once for each job)
            self.assertEqual(mock_scheduler.add_job.call_count, 2)

            # Check that the update_challenges job was added to the scheduler
            update_challenges_job = mock_scheduler.add_job.call_args_list[0]
            self.assertEqual(update_challenges_job[0][0], 'challenges.tasks.update_challenges')
            self.assertEqual(update_challenges_job[1]['seconds'], 60)

            # Check that the update_pet_health job was added to the scheduler
            update_pet_health_job = mock_scheduler.add_job.call_args_list[1]
            self.assertEqual(update_pet_health_job[0][0], 'challenges.tasks.update_pet_health')
            self.assertEqual(update_pet_health_job[1]['seconds'], 15)

            # Check if scheduler.start() is called
            mock_scheduler.start.assert_called_once()

            # Check if atexit.register was called
            mock_atexit_register.assert_called_once()


class TasksTests(TestCase):
    """
    Test suite for tasks defined in challenges/tasks.py.
    This includes testing the functionality of updating challenges,
    resetting missed streaks, and updating pet health.
    """

    def setUp(self) -> None:
        """
        Initialize the test environment.
        This method creates a test user, sets up challenge settings,
        and creates necessary records for testing.
        """
        # Create a test user with default credentials
        self.user = User.objects.create_user(
            username="testuser", password="testpass")

        # Create a profile associated with the user
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user, defaults={"points": 0, "latitude": 0.0, "longitude": 0.0}
        )

        # Get or create a streak record for the user
        self.streak = Streak.objects.get(user=self.user)

        # Configure challenge settings for the tests
        self.challenge_settings = ChallengeSettings.get_solo()
        self.challenge_settings.interval = timedelta(days=1)
        self.challenge_settings.health_depreciation_interval = timedelta(days=1)
        self.challenge_settings.health_depreciation_amount = 5
        self.challenge_settings.save()

        # Create a pet type for the test
        self.pet_type = PetType.objects.create(name="Axolotl")

        # Create a pet for testing the health depreciation functionality
        self.pet = Pet.objects.create(
            name="TestPet",
            owner=self.user,
            health=100,
            type=self.pet_type
        )

    def test_update_challenges(self) -> None:
        """
        Verifies that the update_challenges task correctly calls both
        reset_missed_streaks and cleanup_user_feature_reaches functions.
        """
        with patch('challenges.tasks.reset_missed_streaks') as mock_reset_streaks:
            with patch('challenges.tasks.cleanup_user_feature_reaches') as mock_cleanup:
                update_challenges()

                # Ensure that both functions were called exactly once
                mock_reset_streaks.assert_called_once()
                mock_cleanup.assert_called_once()

    def test_reset_missed_streaks_current_window(self) -> None:
        """
        Verifies that streaks for the current window are not reset.
        Streaks that fall within the current window should maintain their count.
        """
        now = timezone.now()
        current_window_start, _ = get_current_window(now, self.challenge_settings.interval)

        # Set the streak's last window to the current window
        self.streak.last_window = current_window_start
        self.streak.raw_count = 5
        self.streak.save()

        # Call the reset_missed_streaks task
        reset_missed_streaks()

        # Refresh the streak record from the database
        self.streak.refresh_from_db()

        # Assert that the streak count remains unchanged
        self.assertEqual(self.streak.raw_count, 5)

    def test_reset_missed_streaks_previous_window(self) -> None:
        """
        Verifies that streaks from the previous window are not reset.
        Streaks from the previous window should maintain their count.
        """
        now = timezone.now()
        current_window_start, _ = get_current_window(now, self.challenge_settings.interval)
        previous_window_start = current_window_start - self.challenge_settings.interval

        # Set the streak's last window to the previous window
        self.streak.last_window = previous_window_start
        self.streak.raw_count = 5
        self.streak.save()

        # Call the reset_missed_streaks task
        reset_missed_streaks()

        # Refresh the streak record from the database
        self.streak.refresh_from_db()

        # Assert that the streak count remains unchanged
        self.assertEqual(self.streak.raw_count, 5)

    def test_reset_missed_streaks_old_window(self) -> None:
        """
        Verifies that streaks from an older window (not current or previous) are reset.
        Streaks that fall outside the current or previous window should be reset.
        """
        now = timezone.now()
        current_window_start, _ = get_current_window(now, self.challenge_settings.interval)
        old_window_start = current_window_start - (self.challenge_settings.interval * 2)

        # Set the streak's last window to an old window
        self.streak.last_window = old_window_start
        self.streak.raw_count = 5
        self.streak.save()

        # Call the reset_missed_streaks task
        reset_missed_streaks()

        # Refresh the streak record from the database
        self.streak.refresh_from_db()

        # Assert that the streak count is reset to 0
        self.assertEqual(self.streak.raw_count, 0)

    def test_update_pet_health_no_update_needed(self) -> None:
        """
        Verifies that pet health is not updated if the health depreciation
        interval has not passed.
        """
        # Set the last health depreciation to be recent
        self.challenge_settings.last_health_depreciation = timezone.now() - timedelta(hours=12)
        self.challenge_settings.save()

        # Set initial pet health
        self.pet.health = 90
        self.pet.save()

        # Call the update_pet_health task
        update_pet_health()

        # Refresh the pet record from the database
        self.pet.refresh_from_db()

        # Assert that pet health remains unchanged
        self.assertEqual(self.pet.health, 90)

    def test_update_pet_health_update_needed(self) -> None:
        """
        Verifies that pet health is updated if the health depreciation interval
        has passed.
        """
        # Set the last health depreciation to be older
        self.challenge_settings.last_health_depreciation = timezone.now() - timedelta(days=2)
        self.challenge_settings.save()

        # Set initial pet health
        self.pet.health = 90
        self.pet.save()

        # Call the update_pet_health task
        update_pet_health()

        # Refresh the pet record from the database
        self.pet.refresh_from_db()

        # Assert that the pet health was decreased by the specified depreciation amount
        self.assertEqual(self.pet.health, 85)

        # Assert that the last health depreciation timestamp has been updated
        self.challenge_settings.refresh_from_db()
        self.assertGreater(
            self.challenge_settings.last_health_depreciation,
            timezone.now() - timedelta(minutes=1)
        )

    def test_update_pet_health_minimum_zero(self) -> None:
        """
        Verifies that pet health does not fall below zero.
        If health depreciation would result in negative health, it should be set to zero.
        """
        # Set the last health depreciation to be older
        self.challenge_settings.last_health_depreciation = timezone.now() - timedelta(days=2)
        self.challenge_settings.save()

        # Set initial pet health to a value that would go below zero
        self.pet.health = 3
        self.pet.save()

        # Call the update_pet_health task
        update_pet_health()

        # Refresh the pet record from the database
        self.pet.refresh_from_db()

        # Assert that the pet health is set to zero (not negative)
        self.assertEqual(self.pet.health, 0)


class ChallengesViewsTests(TestCase):
    """
    Test suite for the views related to challenges in the challenges app.
    These tests cover functionality related to quiz views and home page views.
    """

    def setUp(self):
        """
        Initialize the test environment for challenge-related views.
        This method creates a test user, a quiz, and associated questions.
        """
        # Create a user for testing purposes
        self.user = get_user_model().objects.create_user(username='testuser', password='password')

        # Create a sample quiz object
        self.quiz = Quiz.objects.create(title="Sample Quiz", total_points=10)

        # Create some questions and choices for the quiz
        question1 = Question.objects.create(quiz=self.quiz, text="What is 2 + 2?")
        Choice.objects.create(question=question1, text="3", is_correct=False)
        Choice.objects.create(question=question1, text="4", is_correct=True)

        question2 = Question.objects.create(quiz=self.quiz, text="What is 3 + 3?")
        Choice.objects.create(question=question2, text="5", is_correct=False)
        Choice.objects.create(question=question2, text="6", is_correct=True)

        # Simulate a user attempting the quiz with answers 'A' and 'B'
        self.quiz_attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            answers='AB',  # Simulated answers where 'A' and 'B' are correct
            score=10.0  # Assign a score for the attempt
        )

        # Setup default location settings for the tests
        LocationsAppSettings.objects.create(default_lat=0.0, default_lon=0.0)

    def test_challenges_home_authenticated(self):
        """
        Verifies that the home page returns the correct context and displays quizzes
        and nearby features when the user is authenticated.
        """
        # Log in the user
        self.client.login(username='testuser', password='password')

        # Access the home page
        response = self.client.get(reverse('challenges:home'))

        # Verify the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that nearby features and quizzes are included in the context
        self.assertIn('nearby_features', response.context)
        self.assertIn('quizzes', response.context)

        # Verify the quiz title appears in the rendered page
        self.assertContains(response, self.quiz.title)

    def test_challenges_home_unauthenticated(self):
        """
        Verifies that the home page returns the correct context and displays quizzes
        and nearby features when the user is not authenticated.
        """
        # Access the home page without logging in
        response = self.client.get(reverse('challenges:home'))

        # Verify the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that nearby features and quizzes are included in the context
        self.assertIn('nearby_features', response.context)
        self.assertIn('quizzes', response.context)

        # Verify the quiz title appears in the rendered page
        self.assertContains(response, self.quiz.title)

    def test_quiz_detail_authenticated(self):
        """
        Verifies that the quiz detail page shows the correct quiz, questions,
        and user answers when the user is authenticated.
        """
        # Log in the user
        self.client.login(username='testuser', password='password')

        # Access the quiz detail page
        response = self.client.get(reverse('challenges:quiz_detail', args=[self.quiz.id]))

        # Verify the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify that the quiz details are included in the context
        self.assertIn('quiz', response.context)
        self.assertEqual(response.context['quiz'].title, 'Sample Quiz')

        # Verify the questions and choices are correctly rendered
        self.assertContains(response, 'What is 2 + 2?')
        self.assertContains(response, '3')
        self.assertContains(response, '4')

        # Verify that the user's answers are included in the context
        self.assertIn('attempt', response.context)
        self.assertEqual(response.context['attempt'].answers, 'AB')

    def test_quiz_detail_invalid_quiz(self):
        """
        Verifies that a 404 error is returned when trying to access a non-existing quiz.
        """
        # Log in the user
        self.client.login(username='testuser', password='password')

        # Try accessing a non-existing quiz
        response = self.client.get(reverse('challenges:quiz_detail', args=[999]))  # Assuming quiz ID 999 doesn't exist

        # Verify the response status code is 404 (Not Found)
        self.assertEqual(response.status_code, 404)

    def test_quiz_attempt_creation(self):
        """
        Verifies that quiz attempts are correctly created and associated with the user.
        """
        self.assertEqual(self.quiz_attempt.user.username, 'testuser')
        self.assertEqual(self.quiz_attempt.quiz.title, 'Sample Quiz')
        self.assertEqual(self.quiz_attempt.answers, 'AB')
        self.assertEqual(self.quiz_attempt.score, 10.0)

    def test_quiz_attempt_score_calculation(self):
        """
        Verifies that the score for a quiz attempt is calculated correctly based on the answers.
        """
        # Check that the score matches the expected value based on the correct answers
        self.assertEqual(self.quiz_attempt.score, self.quiz.total_points)

    def test_quiz_attempt_str(self):
        """
        Verifies that the string representation of a quiz attempt is correct.
        """
        self.assertEqual(str(self.quiz_attempt), f"{self.user} - Sample Quiz (10.0)")
