"""
This module is a Django management command that creates some pet types in the database.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import os

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from pets.models import PetType, Pet, Cosmetic, CosmeticCategory

User = get_user_model()


class Command(BaseCommand):
    """
    This class is a Django management command that creates some pet types in the database.
    """

    help = "Create pet types"

    def handle(self, *args, **kwargs) -> None:
        """
        This function creates an Axolotl, Elephant, and Bat in the database.

        @param args: None expected
        @param kwargs: None expected
        @return: None
        """

        pets = [
            {
                "name": "African Bush Elephant",
                "description": "The African bush elephant (Loxodonta africana) is the largest "
                               "land animal on Earth,  native to the savannas, grasslands, and "
                               "forests of sub-Saharan Africa. It is by its massive size,"
                               " wrinkled gray skin, large fan-shaped ears that help regulate body"
                               " temperature, and long, curved tusks made of ivory.",
                "video": "elephant.webm",
                "cosmetics": [
                    {
                        "name": "Sunglasses",
                        "description": "Vey cool sunglasses",
                        "price": 75,
                        "category": "Glasses",
                        "icon": "glasses.png",
                        "video": "elephantglasses.webm"
                    },
                    {
                        "name": "Plant Hat",
                        "description": "Plant hat",
                        "price": 150,
                        "category": "Hats",
                        "icon": "plant.png",
                        "video": "elephantplant.webm"
                    },
                    {
                        "name": "Cowboy Hat",
                        "description": "Cowboy hat",
                        "price": 100,
                        "category": "Hats",
                        "icon": "cowboy.png",
                        "video": "elephantcowboy.webm"
                    },
                ]
            },

            {
                "name": "Axolotl",
                "description": "The axolotl (Ambystoma mexicanum) is a neotenic salamander "
                               "native to the lakes and canals of Mexico, particularly Lake "
                               "Xochimilco. It is known for its ability to retain juvenile "
                               "features throughout its life, including external gills, "
                               "a wide head, and a fringed, fin-like tail, while also "
                               "possessing remarkable regenerative capabilities that allow it to"
                               " regrow limbs, spinal cord, and even parts of its heart "
                               "and brain.",
                "video": "axolotl.webm",
                "cosmetics": [
                    {
                        "name": "Sunglasses",
                        "description": "Vey cool sunglasses",
                        "price": 75,
                        "category": "Glasses",
                        "icon": "glasses.png",
                        "video": "axolotlglasses.webm"
                    },
                    {
                        "name": "Plant Hat",
                        "description": "Plant hat",
                        "price": 150,
                        "category": "Hats",
                        "icon": "plant.png",
                        "video": "axolotlplant.webm"
                    },
                    {
                        "name": "Cowboy Hat",
                        "description": "Cowboy hat",
                        "price": 100,
                        "category": "Hats",
                        "icon": "cowboy.png",
                        "video": "axolotlcowboy.webm"
                    },
                ]
            },

            {
                "name": "Virginia Big-Eared Bat",
                "description": "The Virginia big-eared bat (Corynorhinus townsendii virginianus)"
                               " is a rare and federally protected subspecies of Townsend's "
                               "big-eared bat, found in limestone caves and forests of the"
                               " Appalachian region in the eastern United States. It is "
                               "characterized by its oversized, elongated ears, soft "
                               "brownish-gray fur, and strong fidelity to its roosting sites,"
                               " making it highly vulnerable to habitat disturbances "
                               "and environmental changes.",
                "video": "bat.webm",
                "cosmetics": [
                    {
                        "name": "Sunglasses",
                        "description": "Vey cool sunglasses",
                        "price": 75,
                        "category": "Glasses",
                        "icon": "glasses.png",
                        "video": "batglasses.webm"
                    },
                    {
                        "name": "Plant Hat",
                        "description": "Plant hat",
                        "price": 150,
                        "category": "Hats",
                        "icon": "plant.png",
                        "video": "batplant.webm"
                    },
                    {
                        "name": "Cowboy Hat",
                        "description": "Cowboy hat",
                        "price": 100,
                        "category": "Hats",
                        "icon": "cowboy.png",
                        "video": "batcowboy.webm"
                    },
                ]
            },
        ]

        # Create the pets and cosmetics from above dict
        for pet in pets:
            pet_type = PetType(
                name=pet["name"],
                description=pet["description"],
            )

            vid = os.path.join(
                os.getcwd(),
                "pets/management/commands/media/videos",
                pet["video"]
            )

            with open(vid, "rb") as f:
                pet_type.base_video = File(f, name=pet["video"])

                try:
                    pet_type.save()
                    self.stderr.write(self.style.SUCCESS(f"Created {pet['name']}"))
                except IntegrityError as e:
                    self.stderr.write(self.style.WARNING(
                        f"Could not create {pet['name']}, skipping it: {str(e)}"))

            for cosmetic_data in pet["cosmetics"]:
                cosmetic = Cosmetic(name=cosmetic_data["name"],
                                    description=cosmetic_data["description"],
                                    price=cosmetic_data["price"])

                icon = os.path.join(
                    os.getcwd(),
                    "pets/management/commands/media/cosmetic_icons",
                    cosmetic_data["icon"]
                )

                with open(icon, "rb") as icon_f:
                    cosmetic.icon = File(icon_f, name=cosmetic_data["icon"])

                    vid = os.path.join(
                        os.getcwd(),
                        "pets/management/commands/media/videos",
                        cosmetic_data["video"]
                    )

                    with open(vid, "rb") as vid_f:
                        cosmetic.video = File(vid_f, name=cosmetic_data["video"])

                        try:
                            category = CosmeticCategory.objects.get(name=cosmetic_data["category"])
                        except CosmeticCategory.DoesNotExist:
                            new_category = CosmeticCategory(name=cosmetic_data["category"])
                            new_category.save()
                            category = new_category

                        cosmetic.category = category
                        cosmetic.fits = PetType.objects.get(name=pet["name"])

                        try:
                            cosmetic.save()
                            msg = f"Created {cosmetic_data['name']} for {pet['name']}"
                            self.stderr.write(self.style.SUCCESS(msg))
                        except IntegrityError as e:
                            msg = (f"Could not create {cosmetic_data['name']} "
                                   f"for {pet['name']}, skipping it: {str(e)}")
                            self.stderr.write(self.style.WARNING(msg))


        # Create example user and default pet
        try:
            example_user = User.objects.create_user(username="ExampleUser", password="example")
            example_user.save()

            default_pet = Pet(name="Default Pet", type=PetType.objects.first())
            default_pet.owner = example_user
            default_pet.save()

            self.stderr.write(self.style.SUCCESS("Created default pet and user"))
        except IntegrityError as e:
            self.stderr.write(self.style.WARNING(f"Could not create default pet or user: {str(e)}"))
