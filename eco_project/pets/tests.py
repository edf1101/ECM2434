from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
from users.models import Profile

class PetTypeTestCase(TestCase):

    def PetSetUp(self):
        """
        Creation of PetType instance
        """
        PetType.objects.create( name = "Axolotl",
                                description = "Critically endangered aquatic species native only to the freshwater of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
                                base_image = SimpleUploadedFile("axolotl.jpg", b"file content", content_type = "image/jpeg"), #dummy image (axolotl.jpg) needed
        )
        axolotl = PetType.objects.get(name = "Axolotl")
        self.assertEqual(axolotl.name, "Axolotl")
        self.assertEqual(axolotl.description, "Critically endangered aquatic species native only to the freshwater of Lake Xochimilco and Lake Chalco in the Valley of Mexico.")
        self.assertTrue(axolotl.base_image)

    def test_pet_str_method(self):
        """
        Tests the __str__ method of PetType
        """
        PetType.objects.create( name = "Axolotl",
                                description = "Critically endangered aquatic species native only to the freshwater of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
                                base_image = SimpleUploadedFile("axolotl.jpg", b"file content", content_type = "image/jpeg"), #dummy image (axolotl.jpg) needed
        )
        axolotl = PetType.objects.get(name = "Axolotl")
        self.assertEqual(str(axolotl), "Axolotl")

class CosmeticTypeTestCase(TestCase):

    def cosmeticSetUp(self):
        """
        Creation of cosmetic object for Pet
        """
        CosmeticType.objects.create(name = "Hat",
                                    x = 5,
                                    y = 20
        )
        hat = CosmeticType.objects.get(name = "Hat")
        self.assertEqual(hat.name, "Hat")
        self.assertEqual(hat.x, 5)
        self.assertEqual(hat.y, 20)

    def test_cosmetic_str_method(self):
        """
        Tests the __str__ method of CosmeticType
        """
        CosmeticType.objects.create(name = "Hat",
                                    x = 5,
                                    y = 20
        )
        hat = CosmeticType.objects.get(name = "Hat")
        self.assertEqual(str(hat), "Hat")

class CosmeticModelTestCase(TestCase):

    def setUp(self):
        self.pet_type = PetType.objects.create( name = "Axolotl",
                                description = "Critically endangered aquatic species native only to the freshwater of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
                                base_image = SimpleUploadedFile("axolotl.jpg", b"file content", content_type = "image/jpeg"), #dummy image (axolotl.jpg) needed
        )
        self.cosmetic_type = CosmeticType.objects.create(name = "Hat",
                                    x = 5,
                                    y = 20
        )
    
    def test_cosmetic_setUp(self):
        hat = Cosmetic.objects.create(name = "Hat", description = "Red stylish hat", type = self.cosmetic_type)
        hat.fits.add(self.pet)
        self.assertEqual(hat.name, "Hat")
        self.assertEqual(hat.description, "Red stylish hat")
        self.assertEqual(hat.type, self.cosmetic_type)
        self.assertIn(self.pet, hat.fits.all())

    def test_cosmetic_str_method(self):
        """
        Tests the __str__ method of Cosmetic
        """
        hat = Cosmetic.objects.create(name = "Hat", description = "Red stylish hat", type = self.cosmetic_type)
        self.assertEqual(str(hat), "Red stylish hat (Hat)")

class PetModelTestCase(TestCase):

    def setUp(self):
        self.profile = Profile.objects.create(name = "Test user")
        self.pet_type = PetType.objects.create( name = "Axolotl",
                                    description = "Critically endangered aquatic species native only to the freshwater of Lake Xochimilco and Lake Chalco in the Valley of Mexico.",
                                    base_image = SimpleUploadedFile("axolotl.jpg", b"file content", content_type = "image/jpeg")
        )
    
    def test_pet_setUp(self):
        axolotl = Pet.objects.create(
            name = "Axo",
            type = self.pet_type,
            owner = self.profile
        )
        self.assertEqual(axolotl.name, "Axo")
        self.assertEqual(axolotl.type, self.pet_type)
        self.assertEqual(axolotl.owner, self.profile)
        self.assertEqual(axolotl.health, 100)
    
    def test_pet_str_method(self):
        axolotl = Pet.objects.create(
            name = "Axo",
            type = self.pet_type,
            owner = self.profile
        )
        self.assertEqual(str(axolotl), "Test user's Axo (Axolotl)")

