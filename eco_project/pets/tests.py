"""
Test Suite for the pets app.
Ensures that each model, Pet and Cosmetic, is created with the appropriate attributes
and that the methods of each model run correctly.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import PetType, CosmeticType, Cosmetic, Pet

User = get_user_model()


class PetTypeTestCase(TestCase):
    """
    Set up for PetType model.
    Ensures that the PetType and its appropraite attirbutes are created and its associated
    methods run appropriately.
    """

    def pet_set_up(self) -> None:
        """
        Creation of PetType instance including name, description, and image.

        @return: None
        """

        PetType.objects.create(
            name="Axolotl",
            description="Critically endangered aquatic species native only to the freshwater of"
                        " Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
            base_image=SimpleUploadedFile(
                "axolotl.jpg", b"file content", content_type="image/jpeg"
            ),
            # dummy image (axolotl.jpg) needed
        )
        axolotl = PetType.objects.get(name="Axolotl")
        self.assertEqual(axolotl.name, "Axolotl")
        self.assertEqual(
            axolotl.description,
            "Critically endangered aquatic species native only to the freshwater"
            " of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
        )
        self.assertTrue(axolotl.base_image)

    def tearDown(self) -> None:
        """
        Clean up any PetType image files created in setUp.

        @return: None
        """
        # Loop through all PetType instances and delete the file on disk if it
        # exists.
        for pet in PetType.objects.all():
            if pet.base_image and os.path.exists(pet.base_image.path):
                try:
                    os.remove(pet.base_image.path)
                except OSError:
                    pass
        super().tearDown()

    def test_pet_str_method(self) -> None:
        """
        Tests the __str__ method of PetType, ensuring that the correct name of the
        PetType is returned as str.

        @return: None
        """
        PetType.objects.create(
            name="Axolotl",
            description="Critically endangered aquatic species native only to the freshwater "
                        "of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
            base_image=SimpleUploadedFile(
                "axolotl.jpg", b"file content", content_type="image/jpeg"
            ),
            # dummy image (axolotl.jpg) needed
        )
        axolotl = PetType.objects.get(name="Axolotl")
        self.assertEqual(str(axolotl), "Axolotl")


class CosmeticTypeTestCase(TestCase):
    """
    Test Suite for CosmeticType model, similar to PetType where its appropriate attributes
    and methods are made and run.
    """

    def cosmetic_set_up(self) -> None:
        """
        Creation of cosmetic object for Pet inscluding cosmetic type name and position on
        pet image / canvas.

        @return: None
        """
        CosmeticType.objects.create(name="Hat", x=5, y=20)
        hat = CosmeticType.objects.get(name="Hat")
        self.assertEqual(hat.name, "Hat")
        self.assertEqual(hat.x, 5)
        self.assertEqual(hat.y, 20)

    def test_cosmetic_str_method(self) -> None:
        """
        Tests the __str__ method of CosmeticType

        @return: None
        """
        CosmeticType.objects.create(name="Hat", x=5, y=20)
        hat = CosmeticType.objects.get(name="Hat")
        self.assertEqual(str(hat), "Hat")


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
            base_image=SimpleUploadedFile(
                "axolotl.jpg", b"file content", content_type="image/jpeg"
            ),
            # dummy image (axolotl.jpg) needed
        )
        self.cosmetic_type = CosmeticType.objects.create(name="Hat", x=5, y=20)

    def tearDown(self) -> None:
        """
        Clean up any PetType image files created in setUp.

        @return: None
        """
        # Clean up any PetType image files created in setUp.
        for pet in PetType.objects.all():
            if pet.base_image and os.path.exists(pet.base_image.path):
                try:
                    os.remove(pet.base_image.path)
                except OSError:
                    pass
        super().tearDown()

    def test_cosmetic_set_up(self) -> None:
        """
        Creation of cosmetic object for Pet and addition to pet.

        @return: None
        """
        hat = Cosmetic.objects.create(
            name="Hat", description="Red stylish hat", type=self.cosmetic_type
        )
        hat.fits.add(self.pet_type)
        self.assertEqual(hat.name, "Hat")
        self.assertEqual(hat.description, "Red stylish hat")
        self.assertEqual(hat.type, self.cosmetic_type)
        self.assertIn(self.pet_type, hat.fits.all())

    def test_cosmetic_str_method(self) -> None:
        """
        Tests the __str__ method of accessory.

        @return: None
        """
        hat = Cosmetic.objects.create(
            name="Hat", description="Red stylish hat", type=self.cosmetic_type
        )
        self.assertEqual(str(hat.description), "Red stylish hat")


class PetModelTestCase(TestCase):
    """
    Tests for creation of pet model and its attributes including its type, owner (user)
    and health and str method functionality.
    """

    def setUp(self) -> None:
        """
        Necessary setup for test: pet and proile (user).

        @return: None
        """
        self.user = User.objects.create_user(
            username="testuser", password="password")
        self.pet_type = PetType.objects.create(
            name="Axolotl",
            description="Critically endangered aquatic species native only to the freshwater "
                        "of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
            base_image=SimpleUploadedFile(
                "axolotl.jpg",
                b"file content",
                content_type="image/jpeg"),
        )

    def test_pet_setup(self) -> None:
        """
        Test for setting up pet and its attributes.

        @return: None
        """
        axolotl = Pet.objects.create(
            name="Axo", type=self.pet_type, owner=self.user)
        self.assertEqual(axolotl.name, "Axo")
        self.assertEqual(axolotl.type, self.pet_type)
        self.assertEqual(axolotl.owner, self.user)
        self.assertEqual(axolotl.health, 100)

    def tearDown(self) -> None:
        """
        Clean up any PetType image files created in setUp.

        @return: None
        """
        # Clean up the PetType image file created in setUp.
        for pet in PetType.objects.all():
            if pet.base_image and os.path.exists(pet.base_image.path):
                try:
                    os.remove(pet.base_image.path)
                except OSError:
                    pass
        super().tearDown()

    def test_pet_str_method(self) -> None:
        """
        Test for __str__ method of pet

        @return: None
        """
        axolotl = Pet.objects.create(
            name="Axo", type=self.pet_type, owner=self.user)
        self.assertEqual(str(axolotl), "testuser's Axo (Axolotl)")
