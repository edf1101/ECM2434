"""
This module contains the test suite for the locations app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.urls import reverse

from challenges.models import ChallengeSettings
from .models import FeatureInstance, FeatureType, QuestionAnswer, QuestionFeature, Map3DChunk, \
    LocationsAppSettings, FeatureInstanceTileMap

User = get_user_model()


class ViewsTestCase(TestCase):
    """
    Test suite for the views of the locations app.
    Ensures that each user request returns the correct url (response) and template,
    including when the page does or does not have a question and redirected 
    when the user is not logged in.
    """

    def setUp(self):
        """
        Set up with necessary data for following view tests including feature type, instance,
        question, and user (user name and password)
        """
        self.factory = RequestFactory()
        self.feature_type = FeatureType.objects.create(
            name="Test Feature Type",
            colour="#ffffff",
            description="A dummy feature type",
            generic_img=SimpleUploadedFile("generic.jpg", b"generic content",
                                           content_type="image/jpeg")
        )
        self.feature_instance = FeatureInstance.objects.create(
            slug="test-feature-instance",
            name="Test Feature Instance",
            latitude=0.0,
            longitude=0.0,
            feature=self.feature_type
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        ChallengeSettings.objects.create()

    def test_base_locations(self) -> None:
        """
        Test if returns homepage for the locations app
        
        @return: None
        """
        response = self.client.get(reverse("locations:base"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/location_home.html")
        self.assertIn("feature_type_list", response.context)

    # def test_test_map(self) -> None:
    #     """
    #     Test if returns test map for the locations app
    #
    #     @return: None
    #     """
    #     response = self.client.get(reverse("locations:map"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "locations/test_map.html")

    def test_individual_feature_page_has_question(self) -> None:
        """
        Test if the page displays a feature instance with a question

        @return: None
        """
        self.client.login(username="testuser", password="testpass")

        QuestionFeature.objects.create(
            feature=self.feature_instance,
            question_text="Test question"
        )
        response = self.client.get(
            reverse("locations:individual-feature", args=[self.feature_instance.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/feature_instance_with_q.html")
        self.assertIn("feature_instance", response.context)
        self.assertIn("question", response.context)

    def test_individual_feature_page_no_question(self) -> None:
        """
        Test if the page displays a feature instance without a question

        @return: None
        """
        self.client.login(username="testuser", password="testpass")
        self.feature_instance.questionfeature_set.all().delete()
        response = self.client.get(
            reverse("locations:individual-feature", args=[self.feature_instance.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/feature_instance.html")
        self.assertIn("feature_instance", response.context)
        self.assertIsNone(response.context.get("question"))

    def test_individual_feature_page_user_authenticated(self) -> None:
        """
        Test if the user is directed to a with a specific feature instance page

        @return: None
        """
        self.client.login(username="testuser", password="testpass")
        self.feature_instance.questionfeature_set.all().delete()
        response = self.client.get(
            reverse("locations:individual-feature", args=[self.feature_instance.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/feature_instance.html")
        self.assertIn("feature_instance", response.context)
        self.assertIsNone(response.context.get("question"))

    # def test_generic_feature_page(self) -> None:
    #     """
    #     Test if the page displays a generic feature type

    #     @return: None
    #     """
    #     response = self.client.get(
    #         reverse("locations:generic-feature-list"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "locations/feature_type_list.html")
    #     self.assertIn("feature_type_list", response.context)

    # def test_generic_feature_list(self) -> None:
    #     """
    #     Test if it returns a page with the list of all the generic features types with hyperlinks

    #     @return: None
    #     """
    #     response = self.client.get(reverse("locations:generic-feature-list"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "locations/feature_type_list.html")
    #     self.assertIn("feature_type_list", response.context)


class SignalsTests(TestCase):
    """
    Test suite for the signals of the locations app.
    Ensures that the signals update the min max position, 
    tile feature map, and feature instance qr code correctly.
    """

    def setUp(self) -> None:
        """
        Necessary set up for the following tests including creation of feature type,
        instance, and map

        @return: None
        """
        LocationsAppSettings.get_instance()
        self.feature_type = FeatureType.objects.create(
            name="Test Feature Type",
            colour="#ffffff",
        )
        self.feature_instance = FeatureInstance.objects.create(
            name='Test Feature Instance',
            latitude=0.0,
            longitude=0.0,
            feature=self.feature_type,
        )

    def test_update_min_max_post_save(self) -> None:
        """
        Test the update min max position post save signal

        @return: None
        """
        Map3DChunk.objects.create(
            bottom_left_lat=0.0,
            top_right_lat=2.0,
            bottom_left_lon=0.0,
            top_right_lon=2.0,
            bottom_left_x=0.0,
            top_right_x=2.0,
            bottom_left_y=0.0,
            top_right_y=2.0,
            bottom_left_z=0.0,
            top_right_z=2.0,
        )
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)
        self.feature_instance.latitude = 3.0
        self.feature_instance.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)
        self.feature_instance.latitude = 1.0
        self.feature_instance.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)

    def test_update_tile_feature_map_post_save_map_chunk(self) -> None:
        """
        Test the update tile feature map post save map chunk signal
        
        @return: None
        """
        chunk = Map3DChunk.objects.create(
            bottom_left_lat=0.0,
            top_right_lat=2.0,
            bottom_left_lon=0.0,
            top_right_lon=2.0,
            bottom_left_x=0.0,
            top_right_x=2.0,
            bottom_left_y=0.0,
            top_right_y=2.0,
            bottom_left_z=0.0,
            top_right_z=2.0,
        )
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)
        chunk.bottom_left_lat = 3.0
        chunk.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)
        chunk.bottom_left_lat = 0.0
        chunk.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)

    def test_update_feature_instance_qr_code_post_save(self) -> None:
        """
        Test the update feature instance qr code post save signal

        @return: None
        """
        self.feature_instance.update_qr_code()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)
        self.feature_instance.latitude = 3.0
        self.feature_instance.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)
        self.feature_instance.latitude = 0.0
        self.feature_instance.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)


class ModelsTests(TestCase):
    """
    Test suite for models of location app.
    Ensures that each model can store the appropriate information and can return correct boolean
    and return the correct string representation.
    """

    def setUp(self) -> None:
        """
        Necessary set up for the following tests including creation of feature type,
        instance, and map
        """
        self.feature_type = FeatureType.objects.create(
            name="Test Feature Type",
            colour="#ffffff",
            description="A dummy feature type",
            generic_img=SimpleUploadedFile("generic.jpg", b"generic content",
                                           content_type="image/jpeg")
        )
        self.feature_instance = FeatureInstance.objects.create(
            slug="test-feature-instance",
            name="Test Feature Instance",
            latitude=0.0,
            longitude=0.0,
            feature=self.feature_type
        )
        self.map_chunk = Map3DChunk.objects.create(
            file=SimpleUploadedFile("chunk.dat", b"chunk data",
                                    content_type="application/octet-stream"),
            file_original_name="chunk.dat",
            center_lat=0.0,
            center_lon=0.0,
            bottom_left_lat=0.0,
            bottom_left_lon=0.0,
            top_right_lat=2.0,
            top_right_lon=2.0,
            bottom_left_x=0.0,
            bottom_left_y=0.0,
            bottom_left_z=0.0,
            top_right_x=2.0,
            top_right_y=2.0,
            top_right_z=2.0,
        )
        LocationsAppSettings.get_instance()

    def test_feature_type_str(self) -> None:
        """
        Test the str method of feature type
        
        @return: None
        """
        self.assertEqual(str(self.feature_type), self.feature_type.name)

    def test_feature_instance_has_question_true(self) -> None:
        """
        Test if the feature instance has a question and return appropriate boolean (true)
        
        @return: None
        """
        QuestionFeature.objects.create(
            feature=self.feature_instance,
            question_text="Test question",
        )
        self.assertTrue(self.feature_instance.has_question)

    def test_feature_instance_has_question_false(self) -> None:
        """
        Test if the feature instance has a question and return appropriate boolean (false)
        
        @return: None
        """
        self.assertFalse(self.feature_instance.has_question)

    def test_feature_instance_has_challenge_true(self) -> None:
        """
        Test if the feature instance has a challenge and return appropriate boolean (true)
        
        @return: None
        """
        QuestionFeature.objects.create(
            feature=self.feature_instance,
            question_text="Test question",
        )
        self.assertTrue(self.feature_instance.has_challenge())

    def test_feature_instance_has_challenge_false(self) -> None:
        """
        Test if the feature instance has a challenge and return appropriate boolean (false)
        
        @return: None
        """
        self.assertFalse(self.feature_instance.has_challenge())

    def test_feature_instance_str(self) -> None:
        """
        Test the str method of feature instance
        
        @return: None
        """
        self.assertEqual(str(self.feature_instance),
                         f'{self.feature_type.name} "test-feature-instance"')

    def test_map_chunk_str(self) -> None:
        """
        Test the str method of map chunk
        
        @return: None
        """
        self.assertEqual(str(self.map_chunk), self.map_chunk.file_original_name)

    def test_locations_app_settings_get_instance(self) -> None:
        """
        Test the get instance method of locations app settings

        @return: None
        """
        settings = LocationsAppSettings.get_instance()
        self.assertEqual(settings, LocationsAppSettings.objects.first())

    def test_locations_app_settings_str(self):
        """
        Test the str method of locations app settings
        """
        settings = LocationsAppSettings.get_instance()
        self.assertEqual(str(settings), "Map Settings")

    def test_question_feature_str(self) -> None:
        """
        Test the str method of question feature
        
        @return: None
        """
        question = QuestionFeature.objects.create(
            question_text="Test question",
            feature=self.feature_instance,
        )
        self.assertEqual(str(question), "Test question")

    def test_question_feature_is_valid_answer(self) -> None:
        """
        Test if the answer is valid for a given sample question and return correct boolean
        
        @return: None
        """
        question = QuestionFeature.objects.create(
            question_text="Test question",
            feature=self.feature_instance,
        )
        QuestionAnswer.objects.create(
            question=question,
            choice_text="Test answer",
        )
        self.assertTrue(question.is_valid_answer("Test answer"))

    def test_question_answer_str(self) -> None:
        """
        # Test the str method of question answer
        
        @return: None
        """
        question = QuestionFeature.objects.create(
            question_text="Test question",
            feature=self.feature_instance,
        )
        answer = QuestionAnswer.objects.create(
            question=question,
            choice_text="Test answer",

        )
        self.assertEqual(str(answer), "Test answer")
