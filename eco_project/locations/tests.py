from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User

from .models import FeatureInstance, FeatureType, QuestionFeature, Map3DChunk, LocationsAppSettings, FeatureInstanceTileMap
from challenges.models import ChallengeSettings

class ViewsTestCase(TestCase):
    """
    Test suite for the views of the locations app.
    Ensures that each user request returns the correct url (response) and template, including when the page
    does or does not have a question and redirected when the user is not logged in.
    """

    def setUp(self):
        """
        Set up with necessary data for following view tests including feature type, instance, question,
        and user (user name and password)
        """
        self.factory = RequestFactory()
        self.feature_type = FeatureType.objects.create(
            name = "Test Feature Type",
            colour = "#ffffff",
        )
        self.feature_instance = FeatureInstance.objects.create(
            name = "Test Feature Instance",
            latitude = 0.0,
            longitude = 0.0,
            feature = self.feature_type,
            has_question = False
        )
        # @property
        # def has_question(self):
        #     return self.has_question
        
        # @has_question.setter
        # def has_question(self, value):
        #     self.has_question = value
        self.question = QuestionFeature.objects.create(
            feature = self.feature_type,
            question = "Test question"
        )
        self.user = User.objects.create_user(
            username = "testuser",
            password = "testpass"
            )
        ChallengeSettings.objects.create()

    def test_base_locations(self):
        """
        Test the base locations view.
        """
        response = self.client.get(reverse("locations:location_home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/location_home.html")
        self.assertIn("feature_type_list", response.context)

    def test_test_map(self):
        """
        Test the test map view.
        """
        response = self.client.get(reverse("locations:test_map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/test_map.html")

    def test_individual_feature_page_has_question(self):
        """
        Test the individual feature page with a question
        """
        self.feature_instance.has_question = True
        self.feature_instance.save()
        response = self.client.get(reverse("locations:individual_feature_page", args = [self.feature_instance.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/feature_instance_with_q.html")
        self.assertIn("feature_instance", response.context)
        self.assertIn("question", response.context)

    def test_individual_feature_page_no_question(self):
        """
        Test the individual feature page without a question - shoudl respond differently to pages with question
        """
        self.feature_instance.has_question = False
        self.feature_instance.save()
        response = self.client.get(reverse("locations:individual_feature_page", args = [self.feature_instance.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/feature_instance.html")
        self.assertIn("feature_instance", response.context)
        self.assertIn("question", response.context)
        self.assertEqual(response.context, None)

    def test_individual_feature_page_user_authenticated(self):
        """
        Test the individual feature page when the user is authenticated
        """
        self.client.login(username = "testuser", password = "testpass")
        response = self.client.get(reverse("locations:individual_feature_page", args = [self.feature_instance.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/feature_instance.html")
        self.assertIn("feature_instance", response.context)
        self.assertIn("question", response.context)
        self.assertEqual(response.context, None)
    def test_generic_feature_page(self):
        """
        Test the generic feature page view
        """
        response = self.client.get(reverse("locations:generic_feature_page", args = [self.feature_type.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/generic_feature_page.html")
        self.assertIn("feature_type", response.context)

    def test_generic_feature_list(self):
        """
        Test the generic feature list view
        """
        response = self.client.get(reverse("locations:generic_feature_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "locations/generic_feature_list.html")
        self.assertIn("feature_type_list", response.context)

class SignalsTests(TestCase):

    """
    Test suite for the signals of the locations app.
    Ensures that the signals update the min max position, tile feature map, and feature instance qr code correctly.
    """
    def setUp(self):
        LocationsAppSettings.objects.create()
        self.feature_type = FeatureType.objects.create(
            name = "Test Feature Type",
            colour = "#ffffff",
            )
        self.feature_instance = FeatureInstance.objects.create(
            name = 'Test Feature Instance',
            latitude = 0.0,
            longitude = 0.0,
            feature = self.feature_type,
            )
    
    def test_update_min_max_post_save(self):
        """
        Test the update min max position signal
        """
        chunk = Map3DChunk.objects.create(
            bottom_left_lat = 0.0,
            top_right_lat = 2.0,
            bottom_left_lon = 0.0,
            top_right_lon = 2.0,
            bottom_left_x = 0.0,
            top_right_x = 2.0,
            bottom_left_y = 0.0,
            top_right_y = 2.0,
            bottom_left_z = 0.0,
            top_right_z = 2.0,
            )
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)
        self.feature_instance.latitude = 3.0
        self.feature_instance.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)
        self.feature_instance.latitude = 1.0
        self.feature_instance.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)

    def test_update_tile_feature_map_post_save_map_chunk(self):
        """
        Test the update tile feature map post save map chunk signal
        """
        chunk = Map3DChunk.objects.create(
            bottom_left_lat = 0.0,
            top_right_lat = 2.0,
            bottom_left_lon = 0.0,
            top_right_lon = 2.0,
            bottom_left_x = 0.0,
            top_right_x = 2.0,
            bottom_left_y = 0.0,
            top_right_y = 2.0,
            bottom_left_z = 0.0,
            top_right_z = 2.0,
            )
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)
        chunk.bottom_left_lat = 3.0
        chunk.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 0)
        chunk.bottom_left_lat = 0.0
        chunk.save()
        self.assertEqual(FeatureInstanceTileMap.objects.count(), 1)
        
    def test_update_feature_instance_qr_code_post_save(self):
        """
        Test the update feature instance qr code post save signal
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

    def setUp(self):
        self.feature_type = FeatureType.objects.create(
            name = "Test Feature Type",
            colour = "#ffffff",
        )
        self.feature_instance = FeatureInstance.objects.create(
            name = 'Test Feature Instance',
            latitude = 0.0,
            longitude = 0.0,
            feature = self.feature_type,
            has_question = False
        )
        self.map_chunk = Map3DChunk.objects.create(
            bottom_left_lat = 0.0,
            top_right_lat = 2.0,
            bottom_left_lon = 0.0,
            top_right_lon = 2.0,
            bottom_left_x = 0.0,
            top_right_x = 2.0,
            bottom_left_y = 0.0,
            top_right_y = 2.0,
            bottom_left_z = 0.0,
            top_right_z = 2.0,
        )
        LocationsAppSettings.objects.create()

    def test_feature_instance_str(self):
        self.assertEqual(str(self.feature_instance), self.feature_instance.name)

    def test_feature_type_str(self):
        self.assertEqual(str(self.feature_type), self.feature_type.name)