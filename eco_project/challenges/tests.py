"""
This module is to test the challenges app.
Mocks are used extensively to simplify the tests and to avoid side effects.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import json
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from fontTools.misc.cython import returns

from challenges.challenge_helpers import (
    get_interval,
    get_current_window,
    streak_to_points,
    user_in_range_of_feature,
    user_already_reached_in_window,
    user_reached_feature,
    get_features_near,
)

from challenges.models import (
    ChallengeSettings,
    Streak,
    UserFeatureReach,
    Quiz,
    Question,
    Choice,
    QuizAttempt,
)

from locations.models import FeatureInstance, FeatureType
from pets.models import Pet, PetType
from users.models import Profile

# pylint: disable=W0613,C0415,W0611


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
    @patch("challenges.challenge_helpers.haversine", return_value=1500)
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


class ChallengeHelpersTests(TestCase):
    """
    Tests for the challenge helper functions.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user, defaults={"points": 0, "latitude": 0.0, "longitude": 0.0}
        )
        pet_type = PetType.objects.create(
            name="Axolotl",
            description="Aquatic species native to Mexico.",
            base_video=SimpleUploadedFile(
                "axolotl.webm", b"file content", content_type="video/webm"
            ),
        )
        self.pet = Pet.objects.create(
            name="Axo",
            type=pet_type,
            owner=self.user,
        )

        self.feature_type = FeatureType.objects.create(name="Test Feature Type")
        self.feature_instance = FeatureInstance.objects.create(
            feature=self.feature_type,
            name="Test Feature Instance",
            latitude=0.0,
            longitude=0.0,
            slug="test-feature-instance",
        )
        self.challenge_settings = ChallengeSettings.get_solo()
        self.challenge_settings.interval = timedelta(days=1)
        self.challenge_settings.question_feature_points = 2
        self.challenge_settings.reached_feature_points = 1
        self.challenge_settings.save()

    def test_get_interval(self) -> None:
        """
        Test the get_interval function.
        """
        interval = get_interval()
        self.assertEqual(interval, timedelta(days=1))

        # Test with no ChallengeSettings object
        ChallengeSettings.objects.all().delete()
        interval = get_interval()
        self.assertEqual(interval, timedelta(days=1))

    @patch("challenges.models.ChallengeSettings.objects.first")
    def test_get_interval_no_challenges(self, challenge_settings) -> None:
        """
        Test the get_interval function when there are no challenges
        """
        challenge_settings.side_effect = ChallengeSettings.DoesNotExist

        interval = get_interval()
        self.assertEqual(interval, timedelta(days=1))

    def test_get_current_window(self) -> None:
        """
        Test the get_current_window function.
        """
        now_time = timezone.now()
        interval = timedelta(days=1)
        window_start, window_end = get_current_window(now_time, interval)

        self.assertEqual(window_start.date(), now_time.date())
        self.assertEqual(window_end.date(), now_time.date() + timedelta(days=1))

        interval = timedelta(hours=1)
        window_start, window_end = get_current_window(now_time, interval)
        self.assertEqual(window_start.hour, now_time.hour)
        self.assertEqual(window_end.hour, now_time.hour + 1)

    def test_streak_to_points(self) -> None:
        """
        Test the streak_to_points function.
        """
        self.assertEqual(streak_to_points(1), 5)
        self.assertEqual(streak_to_points(2), 10)
        self.assertEqual(streak_to_points(4), 15)
        self.assertEqual(streak_to_points(8), 20)
        self.assertEqual(streak_to_points(16), 25)

    @patch("challenges.challenge_helpers.haversine", return_value=100)
    def test_user_in_range_of_feature(self, mock_haversine: MagicMock) -> None:
        """
        Test the user_in_range_of_feature function.
        """

        settings.CHECK_USER_CHALLENGE_RANGE = True
        settings.USER_CHALLENGE_RANGE = 200
        self.assertTrue(
            user_in_range_of_feature(self.user, self.feature_instance)
        )

        settings.CHECK_USER_CHALLENGE_RANGE = False
        self.assertTrue(
            user_in_range_of_feature(self.user, self.feature_instance)
        )

    @patch("challenges.models.UserFeatureReach.objects.filter")
    @patch("challenges.challenge_helpers.get_current_window")
    def test_user_already_reached_in_window(
            self, mock_get_current_window: MagicMock, mock_filter: MagicMock
    ) -> None:
        """
        Test the user_already_reached_in_window function.
        """
        mock_get_current_window.return_value = (
            timezone.now(),
            timezone.now() + timedelta(days=1),
        )
        mock_filter.return_value.exists.return_value = True

        self.assertTrue(
            user_already_reached_in_window(
                self.user, self.feature_instance))

        mock_filter.return_value.exists.return_value = False
        self.assertFalse(
            user_already_reached_in_window(
                self.user, self.feature_instance))

    @patch("challenges.challenge_helpers.user_already_reached_in_window", return_value=False)
    @patch("challenges.challenge_helpers.user_in_range_of_feature", return_value=True)
    def test_user_reached_feature(
            self, mock_in_range: MagicMock, mock_already_reached: MagicMock
    ) -> None:
        """
        Test the user_reached_feature function.
        """
        initial_points = self.user.profile.points
        user_reached_feature(self.user, self.feature_instance)
        self.assertEqual(
            self.user.profile.points,
            initial_points + self.challenge_settings.reached_feature_points,
        )

        # test user not in range
        mock_in_range.return_value = False
        user_reached_feature(self.user, self.feature_instance)
        self.assertEqual(
            self.user.profile.points,
            initial_points + self.challenge_settings.reached_feature_points,
        )

        # test user already reached
        mock_in_range.return_value = True
        mock_already_reached.return_value = True
        user_reached_feature(self.user, self.feature_instance)
        self.assertEqual(
            self.user.profile.points,
            initial_points + self.challenge_settings.reached_feature_points,
        )

    @patch("challenges.challenge_helpers.haversine", return_value=100)
    def test_get_features_near(self, mock_haversine: MagicMock) -> None:
        """
        Test the get_features_near function.
        """
        features = get_features_near(0.0, 0.0, user=self.user, specific_feature=True)
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["description"], "Test Feature Instance")

        settings.USER_CHALLENGE_RANGE = 50
        features = get_features_near(0.0, 0.0, user=self.user)
        self.assertNotIn("url", features[0])

        settings.USER_CHALLENGE_RANGE = 200
        features = get_features_near(0.0, 0.0, user=self.user)
        self.assertIn("url", features[0])

class ChallengeSettingsModelTest(TestCase):
    """
    Tests for the ChallengeSettings model.
    """

    def test_challenge_settings_creation(self) -> None:
        """
        Test that a ChallengeSettings object is created correctly.
        """
        settings = ChallengeSettings.get_solo()
        self.assertIsInstance(settings, ChallengeSettings)
        self.assertEqual(
            str(settings), "Challenge Settings"
        )  # Test the __str__ method
        self.assertEqual(
            settings.interval, timedelta(days=1)
        )  # Check default value
        self.assertEqual(settings.question_feature_points, 35)
        self.assertEqual(settings.reached_feature_points, 20)
        self.assertEqual(
            settings.health_depreciation_interval, timedelta(hours=6))
        self.assertEqual(settings.health_depreciation_amount, 2)

    def test_challenge_settings_singleton(self) -> None:
        """
        Test that only one ChallengeSettings object can exist.
        """
        settings1 = ChallengeSettings.get_solo()
        settings2 = ChallengeSettings.get_solo()
        self.assertEqual(settings1, settings2)

        # change a value and check it persists
        settings1.interval = timedelta(days=2)
        settings1.save()
        settings3 = ChallengeSettings.get_solo()
        self.assertEqual(settings3.interval, timedelta(days=2))

    def test_challenge_settings_save(self):
        """
        Test the save method.
        """
        settings = ChallengeSettings()
        settings.save()
        self.assertEqual(settings.pk, 1)


class StreakModelTest(TestCase):
    """
    Tests for the Streak model.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.streak = Streak.objects.create(user=self.user)
        self.challenge_settings = ChallengeSettings.get_solo()
        self.challenge_settings.interval = timedelta(days=1)
        self.challenge_settings.save()

    def test_streak_creation(self) -> None:
        """
        Test that a Streak object is created correctly.
        """
        self.assertIsInstance(self.streak, Streak)
        self.assertEqual(self.streak.user, self.user)
        self.assertEqual(self.streak.raw_count, 0)
        self.assertIsNone(self.streak.last_window)
        self.assertEqual(str(self.streak), "testuser - Streak: 0")

    def test_effective_streak(self) -> None:
        """
        Test the effective_streak property.
        """
        now = timezone.now()
        current_window_start, _ = get_current_window(
            now, self.challenge_settings.interval)

        self.assertEqual(self.streak.effective_streak, 0)  # No last_window

        self.streak.last_window = current_window_start
        self.streak.raw_count = 5
        self.streak.save()
        self.assertEqual(self.streak.effective_streak, 5)  # last_window is current

        self.streak.last_window = current_window_start - \
                                  self.challenge_settings.interval
        self.streak.save()
        self.assertEqual(
            self.streak.effective_streak, 5
        )  # last_window is previous

        self.streak.last_window = current_window_start - \
                                  self.challenge_settings.interval * 2
        self.streak.save()
        self.assertEqual(self.streak.effective_streak,
                         0)  # last_window is too old

    def test_running_out(self) -> None:
        """
        Test the running_out property.
        """
        now = timezone.now()
        current_window_start, _ = get_current_window(
            now, self.challenge_settings.interval)

        self.assertFalse(self.streak.running_out)  # No streak

        self.streak.raw_count = 1
        self.streak.last_window = current_window_start - \
                                  self.challenge_settings.interval
        self.streak.save()
        self.assertTrue(self.streak.running_out)  # Streak, last window != current

        self.streak.last_window = current_window_start
        self.streak.save()
        self.assertFalse(
            self.streak.running_out
        )  # Streak, last window == current


class UserFeatureReachModelTest(TestCase):
    """
    Tests for the UserFeatureReach model.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.feature_type = FeatureType.objects.create(
            name="Test Feature Type")
        self.feature_instance = FeatureInstance.objects.create(
            feature=self.feature_type,
            name="Test Feature Instance",
            latitude=0.0,
            longitude=0.0,
            slug="test-feature-instance",
        )
        self.user_feature_reach = UserFeatureReach.objects.create(
            user=self.user, feature_instance=self.feature_instance
        )

    def test_user_feature_reach_creation(self) -> None:
        """
        Test that a UserFeatureReach object is created correctly.
        """
        self.assertIsInstance(self.user_feature_reach, UserFeatureReach)
        self.assertEqual(self.user_feature_reach.user, self.user)
        self.assertEqual(
            self.user_feature_reach.feature_instance, self.feature_instance
        )
        self.assertIsNotNone(self.user_feature_reach.reached_at)
        self.assertEqual(
            str(self.user_feature_reach),
            f"{self.user.username} reached {self.feature_instance} at {self.user_feature_reach.reached_at}",
        )

    def test_extra_field(self):
        """
        Test the extra field.
        """
        reach = UserFeatureReach.objects.create(
            user=self.user, feature_instance=self.feature_instance, extra="extra_data")
        self.assertEqual(reach.extra, "extra_data")


class QuizModelTest(TestCase):
    """
    Tests for the Quiz model.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.quiz = Quiz.objects.create(title="Test Quiz", total_points=20)

    def test_quiz_creation(self) -> None:
        """
        Test that a Quiz object is created correctly.
        """
        self.assertIsInstance(self.quiz, Quiz)
        self.assertEqual(self.quiz.title, "Test Quiz")
        self.assertEqual(self.quiz.total_points, 20)
        self.assertEqual(str(self.quiz), "Test Quiz")


class QuestionModelTest(TestCase):
    """
    Tests for the Question model.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.question = Question.objects.create(
            quiz=self.quiz, text="Test Question")

    def test_question_creation(self) -> None:
        """
        Test that a Question object is created correctly.
        """
        self.assertIsInstance(self.question, Question)
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertEqual(self.question.text, "Test Question")
        self.assertEqual(str(self.question), "Test Question")


class ChoiceModelTest(TestCase):
    """
    Tests for the Choice model.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.question = Question.objects.create(
            quiz=self.quiz, text="Test Question")
        self.choice = Choice.objects.create(
            question=self.question, text="Test Choice", is_correct=True)

    def test_choice_creation(self) -> None:
        """
        Test that a Choice object is created correctly.
        """
        self.assertIsInstance(self.choice, Choice)
        self.assertEqual(self.choice.question, self.question)
        self.assertEqual(self.choice.text, "Test Choice")
        self.assertTrue(self.choice.is_correct)
        self.assertEqual(str(self.choice), "Test Choice")


class QuizAttemptModelTest(TestCase):
    """
    Tests for the QuizAttempt model.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.attempt = QuizAttempt.objects.create(
            user=self.user, quiz=self.quiz, answers="ABC", score=15.5
        )

    def test_quiz_attempt_creation(self) -> None:
        """
        Test that a QuizAttempt object is created correctly.
        """
        self.assertIsInstance(self.attempt, QuizAttempt)
        self.assertEqual(self.attempt.user, self.user)
        self.assertEqual(self.attempt.quiz, self.quiz)
        self.assertEqual(self.attempt.answers, "ABC")
        self.assertEqual(self.attempt.score, 15.5)
        self.assertIsNotNone(self.attempt.timestamp)
        self.assertEqual(
            str(self.attempt), f"{self.user} - {self.quiz} (15.5)"
        )
