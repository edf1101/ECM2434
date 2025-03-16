"""
This module is a Django management command that creates some pet types in the database.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import os
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from pets.models import PetType


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

        pets = [{"name": "African Bush Elephant",
                 "description": "The African bush elephant (Loxodonta africana) is the largest "
                                "land animal on Earth,  native to the savannas, grasslands, and "
                                "forests of sub-Saharan Africa. It is by its massive size,"
                                " wrinkled gray skin, large fan-shaped ears that help regulate body"
                                " temperature, and long, curved tusks made of ivory.",
                 "image": "elephant.png",
                 "video": "elephant.webm",
                 },

                {"name": "Axolotl",
                 "description": "The axolotl (Ambystoma mexicanum) is a neotenic salamander "
                                "native to the lakes and canals of Mexico, particularly Lake "
                                "Xochimilco. It is known for its ability to retain juvenile "
                                "features throughout its life, including external gills, "
                                "a wide head, and a fringed, fin-like tail, while also "
                                "possessing remarkable regenerative capabilities that allow it to"
                                " regrow limbs, spinal cord, and even parts of its heart "
                                "and brain.",
                 "image": "axolotl.png",
                 "video": "axolotl.webm",
                 },

                {"name": "Virginia Big-Eared Bat",
                 "description": "The Virginia big-eared bat (Corynorhinus townsendii virginianus)"
                                " is a rare and federally protected subspecies of Townsend's "
                                "big-eared bat, found in limestone caves and forests of the"
                                " Appalachian region in the eastern United States. It is "
                                "characterized by its oversized, elongated ears, soft "
                                "brownish-gray fur, and strong fidelity to its roosting sites,"
                                " making it highly vulnerable to habitat disturbances "
                                "and environmental changes.",
                 "image": "bat.png",
                 "video": "bat.webm",
                 },
                ]

        # Empty pet media directory beforehand to reduce clutter in there
        img_folder = os.path.join(settings.MEDIA_ROOT, "pets/base_imgs")
        vid_folder = os.path.join(settings.MEDIA_ROOT, "pets/videos")

        # Check if the folder exists
        if os.path.exists(img_folder):
            # Remove everything in the folder
            for file in os.listdir(img_folder):
                os.remove(os.path.join(img_folder, file))

        if os.path.exists(vid_folder):
            # Remove everything in the folder
            for file in os.listdir(vid_folder):
                os.remove(os.path.join(vid_folder, file))

        for pet in pets:
            pet_type = PetType(
                name=pet["name"],
                description=pet["description"],
            )

            img = os.path.join(
                os.getcwd(),
                "pets/management/commands/pet_images",
                pet["image"])

            vid = os.path.join(
                os.getcwd(),
                "pets/management/commands/pet_videos",
                pet["video"]
            )

            with open(img, "rb") as f:
                pet_type.base_image = File(f, name=pet["image"])
                with open(vid, "rb") as vid_f:
                    pet_type.video = File(vid_f, name=pet["video"])
                    try:
                        pet_type.save()
                        self.stderr.write(self.style.SUCCESS(f"Created {pet['name']}"))
                    except IntegrityError as e:
                        self.stderr.write(self.style.WARNING(
                            f"Could not create {pet['name']}, skipping it: {str(e)}"))
