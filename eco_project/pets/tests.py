"""
Test Suite for the pets app.
Ensures that each model, Pet and Cosmetic, is created with the appropriate attributes
and that the methods of each model run correctly.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

import os

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import PetType, CosmeticType, Cosmetic, Pet

User = get_user_model()


class PetTypeTestCase(TestCase):
    """
    Set up for PetType model.
    Ensures that the PetType and its appropriate attributes are created and its associated
    methods run appropriately.
    """

    def setUp(self) -> None:
        """
        Creation of PetType instance including name, description, and video.

        @return: None
        """

        self.pet_type = PetType.objects.create(
            name="Axolotl",
            description="Critically endangered aquatic species native only to the freshwater of"
                        " Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
            video=SimpleUploadedFile(
                "axolotl.webm", b"file content", content_type="video/webm"
            ),
        )

        self.assertEqual(self.pet_type.name, "Axolotl")
        self.assertEqual(
            self.pet_type.description,
            "Critically endangered aquatic species native only to the freshwater"
            " of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
        )
        self.assertTrue(self.pet_type.video)

    def tearDown(self) -> None:
        """
        Clean up any PetType video files created in setUp.

        @return: None
        """
        # Loop through all PetType instances and delete the file on disk if it
        # exists.
        for pet in PetType.objects.all():
            if pet.video and os.path.exists(pet.video.path):
                try:
                    os.remove(pet.video.path)
                except OSError:
                    pass
        super().tearDown()

    def test_pet_str_method(self) -> None:
        """
        Tests the __str__ method of PetType, ensuring that the correct name of the
        PetType is returned as str.

        @return: None
        """

        self.assertEqual(self.pet_type.__str__(), "Axolotl")


class CosmeticTypeTestCase(TestCase):
    """
    Test Suite for CosmeticType model, similar to PetType where its appropriate attributes
    and methods are made and run.
    """

    def cosmetic_set_up(self) -> None:
        """
        Creation of cosmetic object for Pet

        @return: None
        """
        CosmeticType.objects.create(name="Hat")
        hat = CosmeticType.objects.get(name="Hat")
        self.assertEqual(hat.name, "Hat")

    def test_cosmetic_str_method(self) -> None:
        """
        Tests the __str__ method of CosmeticType

        @return: None
        """
        CosmeticType.objects.create(name="Hat")
        hat = CosmeticType.objects.get(name="Hat")
        self.assertEqual(hat.__str__(), "Hat")


class CosmeticModelTestCase(TestCase):
    """
    Test for cosmetic object on pet model including accessory setup on pet object and str method.
    """

    def setUp(self) -> None:
        """
        Set up with necessary data for PetType and CosmeticType objects.

        @return: None
        """
        self.pet_type = PetType.objects.create(
            name="Axolotl",
            description="Critically endangered aquatic species native only to the freshwater "
                        "of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
            video=SimpleUploadedFile(
                "axolotl.webm", b"file content", content_type="video/webm"
            ),
        )
        self.cosmetic_type = CosmeticType.objects.create(name="Hat")

    def tearDown(self) -> None:
        """
        Clean up any PetType video files created in setUp.

        @return: None
        """

        # Clean up any PetType video files created in setUp.
        for pet in PetType.objects.all():
            if pet.video and os.path.exists(pet.video.path):
                try:
                    os.remove(pet.video.path)
                except OSError:
                    pass
        super().tearDown()

    def test_cosmetic_set_up(self) -> None:
        """
        Creation of cosmetic object for Pet and addition to pet.

        @return: None
        """
        hat = Cosmetic.objects.create(
            name="Hat", description="Red stylish hat", type=self.cosmetic_type, price=10
        )
        hat.fits.add(self.pet_type)
        self.assertEqual(hat.name, "Hat")
        self.assertEqual(hat.description, "Red stylish hat")
        self.assertEqual(hat.type, self.cosmetic_type)
        self.assertEqual(hat.price, 10)
        self.assertIn(self.pet_type, hat.fits.all())

    def test_cosmetic_str_method(self) -> None:
        """
        Tests the __str__ method of accessory.

        @return: None
        """
        hat = Cosmetic.objects.create(
            name="Red Hat", description="Red stylish hat", type=self.cosmetic_type, price=10
        )
        self.assertEqual(hat.__str__(), "Red Hat (Hat)")


class PetModelTestCase(TestCase):
    """
    Tests for creation of pet model and its attributes including its type, owner (user)
    and health and str method functionality.
    """

    def setUp(self) -> None:
        """
        Necessary setup for test: pet and profile (user).

        @return: None
        """
        self.user = User.objects.create_user(
            username="testuser", password="password")

        self.pet_type = PetType.objects.create(
            name="Axolotl",
            description="Critically endangered aquatic species native only to the freshwater "
                        "of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
            video=SimpleUploadedFile(
                "axolotl.webm",
                b"file content",
                content_type="video/webm"),
        )

        self.pet = Pet.objects.create(
            name="Axo", type=self.pet_type, owner=self.user)

    def test_pet_setup(self) -> None:
        """
        Test for setting up pet and its attributes.

        @return: None
        """
        self.assertEqual(self.pet.name, "Axo")
        self.assertEqual(self.pet.type, self.pet_type)
        self.assertEqual(self.pet.owner, self.user)
        self.assertEqual(self.pet.health, 100)

    def test_pet_str_method(self) -> None:
        """
        Test for __str__ method of pet

        @return: None
        """
        self.assertEqual(str(self.pet), "testuser's Axo (Axolotl)")

    def test_get_pet_data(self):
        """
        Test for the get_pet_data api endpoint

        @return: None
        """
        url = reverse("pets:get_pet_data", args=[self.user.username])
        response = self.client.post(url)
        data = response.json()

        self.assertEqual(data["user_points"], self.user.profile.points)
        self.assertEqual(data["pet_name"], self.pet.name)

    def test_get_pet_data_user_not_found(self):
        """
        Test for the get_pet_data api endpoint

        @return: None
        """
        url = reverse("pets:get_pet_data", args=["nonexistentuser"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "User not found."})

    def test_get_pet_data_no_pet(self):
        """
        Test for the get_pet_data api endpoint

        @return: None
        """
        self.pet.delete()
        url = reverse("pets:get_pet_data", args=[self.user.username])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "No pet found for this user."})

    def tearDown(self) -> None:
        """
        Clean up any PetType video files created in setUp.

        @return: None
        """
        # Clean up the PetType video file created in setUp.
        for pet in PetType.objects.all():
            if pet.video and os.path.exists(pet.video.path):
                try:
                    os.remove(pet.video.path)
                except OSError:
                    pass
        super().tearDown()


class NotifyLowHealthSignalTestCase(TestCase):
    def setUp(self):
        """
        Set up a user, pet type, and pet instance for testing.
        """
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")
        self.pet_type = PetType.objects.create(
            name="Axolotl",
            description="Aquatic species native to Mexico.",
        )
        self.pet = Pet.objects.create(
            name="Axo",
            type=self.pet_type,
            owner=self.user,
            health=100,
            low_health_notified=False,
        )

    def test_notify_low_health_signal_sends_email(self):
        """
        Test that an email is sent when pet health drops below 25%.
        """
        self.pet.health = 20
        self.pet.save()

        # Check that an email has been sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Your pet needs help!", mail.outbox[0].subject)
        self.assertIn("Your pet Axo's health has dropped below 25%", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        # Check that low_health_notified flag is set to True
        self.pet.refresh_from_db()
        self.assertTrue(self.pet.low_health_notified)

    def test_notify_low_health_signal_does_not_send_duplicate_email(self):
        """
        Test that no duplicate email is sent if low_health_notified is already True.
        """
        self.pet.health = 20
        self.pet.low_health_notified = True
        self.pet.save()

        # Check that no new email is sent
        self.assertEqual(len(mail.outbox), 0)

    def test_notify_low_health_signal_resets_flag(self):
        """
        Test that the low_health_notified flag resets when health is restored to 25% or above.
        """
        self.pet.health = 10
        self.pet.save()
        self.pet.refresh_from_db()
        self.assertTrue(self.pet.low_health_notified)

        self.pet.health = 30
        self.pet.save()

        self.pet.refresh_from_db()
        self.assertFalse(self.pet.low_health_notified)


class PetViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        self.pet_type = PetType.objects.create(
            name="Axolotl",
            description="Aquatic species native to Mexico.",
            video=SimpleUploadedFile(
                "axolotl.webm", b"file content", content_type="video/webm"
            ),
        )

        self.pet = Pet.objects.create(
            name="Axo",
            type=self.pet_type,
            owner=self.user,
        )

    def test_view_pet(self):
        response = self.client.get(reverse("pets:mypet"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pets/mypet.html")
        self.assertEqual(response.context["pet"], self.pet)

    def test_equip_cosmetic(self):
        cosmetic_type = CosmeticType.objects.create(name="Hat")
        cosmetic = Cosmetic.objects.create(name="Red Hat", type=cosmetic_type, price=10)
        self.user.profile.owned_accessories.add(cosmetic)
        response = self.client.get(reverse("pets:equip_cosmetic", args=[cosmetic.id, 1]))
        self.assertRedirects(response, reverse("pets:mypet"))
        self.assertIn(cosmetic, self.pet.cosmetics.all())

    def test_shop_view(self):
        response = self.client.get(reverse("pets:shop"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pets/shop.html")
