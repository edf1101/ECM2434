"""
This script is used to import 3D map chunk data into the database.
It would be a long manual process to import all ~400 chunks into the database so this script
automates it. There must be the console_out.txt file from blender in the same directory as this
script and the exports folder with all the .glb files in the same directory as this script.
"""
import os
from random import choice
from typing import Any

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from locations.models import Map3DChunk, LocationsAppSettings


def get_mesh_data_from_file() -> dict[str, dict[str, Any]]:
    """
    This function reads the console_out.txt file and extracts the data from it about all the
    3D map chunks.

    :return: A dictionary with the relevant data for each 3D map chunk.
    """
    path_to_console_out: str = os.path.join(os.getcwd(),
                                            "locations/management/commands/console_out.txt")
    console_read = open(path_to_console_out, "r")
    console_lines = console_read.readlines()

    data: dict[str, dict[str, Any]] = {}  # dict to store the data

    # These are the geodesic coordinates of the center, bottom left and top right of the chunk
    center_deg = (0, 0)
    bottom_left_deg = (0, 0)
    top_right_deg = (0, 0)

    # These are the 3d blender coordinates of the bottom left and top right of the chunk
    bottom_left_blender = (0, 0, 0)
    top_right_blender = (0, 0, 0)

    for line in console_lines:
        if "{'center'" in line:  # if the line contains the center coordinates of the chunk
            d = line.split("(")[1:]
            for i in range(len(d)):
                d[i] = d[i].split(")")[0]

            center = d[0].split(", ")
            bottom_left = d[1].split(", ")
            top_right = d[2].split(", ")
            # convert to float tuples
            center_deg = (round(float(center[0]), 5), round(float(center[1]), 5))
            bottom_left_deg = (round(float(bottom_left[0]), 5), round(float(bottom_left[1]), 5))
            top_right_deg = (round(float(top_right[0]), 5), round(float(top_right[1]), 5))

        if "Tile center in" in line:  # if the line contains the blender coordinates of the chunk
            t = line.split("((")[1:]

            for i in range(len(t)):
                t[i] = t[i].split("))")[0]

            bottom_left = t[0].split(", ")
            top_right = t[1].split(", ")
            # convert to float tuples
            bottom_left_blender = (
                round(float(bottom_left[0]), 3), round(float(bottom_left[1]), 3),
                round(float(bottom_left[2]), 3))
            top_right_blender = (
                round(float(top_right[0]), 3), round(float(top_right[1]), 3),
                round(float(top_right[2]), 3))

        if "Imported object" in line:  # if the line contains the name of the chunk
            obj_name = line.split("(")[1].split(")")[0].replace('"', "")
            data[obj_name] = {"center_deg": center_deg, "bottom_left_deg": bottom_left_deg,
                              "top_right_deg": top_right_deg,
                              "bottom_left_blender": bottom_left_blender,
                              "top_right_blender": top_right_blender}

    return data


class Command(BaseCommand):
    """
    This script is used to import 3D map chunk data into the database.
    """
    help = "Import 3D map chunk data into the database"

    def handle(self, *args, **kwargs) -> None:
        """
        This function is called when the import_chunks script is run.

        :param args:  None expected
        :param kwargs: None expected
        :return: None
        """

        chunk_dict = get_mesh_data_from_file()
        # clear the Map3D chunks table
        path_to_exports: str = os.path.join(os.getcwd(),
                                            "locations/management/commands/exports/")
        Map3DChunk.objects.all().delete()
        # import all the chunks from the dict
        chunks = []
        for name, data in chunk_dict.items():
            file_path: str = os.path.join(path_to_exports, f'{name}.glb')

            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            with open(file_path, 'rb') as f:
                file = File(f)  # Create a Django file object

                # Save it with a safe path so that unsafe error isn't raised
                safe_file_path = default_storage.save(f'locations/3d_map_chunks/{name}.glb', file)

                # Create Map3DChunk instance and add it to the list
                chunks.append(Map3DChunk(
                    file_original_name=f'{name}.glb',
                    center_lat=data['center_deg'][0],
                    center_lon=data['center_deg'][1],
                    bottom_left_lat=data['bottom_left_deg'][0],
                    bottom_left_lon=data['bottom_left_deg'][1],
                    top_right_lat=data['top_right_deg'][0],
                    top_right_lon=data['top_right_deg'][1],
                    bottom_left_x=data['bottom_left_blender'][0],
                    bottom_left_y=data['bottom_left_blender'][1],
                    bottom_left_z=data['bottom_left_blender'][2],
                    top_right_x=data['top_right_blender'][0],
                    top_right_y=data['top_right_blender'][1],
                    top_right_z=data['top_right_blender'][2],
                    file=safe_file_path  # Attach the saved file
                ))

        for chunk in chunks:
            chunk.save()

        self.stdout.write(self.style.SUCCESS(f"Saved {len(chunk_dict)} chunks to database"))

        image_path = os.path.join(os.getcwd(),
                                  "locations/management/commands/heightmap.png")
        # create some random letters to make the file name unique
        letters = ''.join([choice('1234567890ABCDEF') for i in range(5)])

        img_file = None
        with open(image_path, 'rb') as f:
            file = File(f)  # Create a Django file object

            # Save it with a safe path so that unsafe error isn't raised
            img_file = default_storage.save(
                f'locations/camera_z_map/camera_height_map{letters}.png', file)

        # Save the image path to the settings
        settings = LocationsAppSettings.get_instance()
        settings.camera_z_map = img_file

        # set the colour and the render dist
        settings.world_colour = '#106A1A'
        settings.render_dist = 250
        settings.default_lat, settings.default_lon = 50.73585506490216, -3.534556667162146

        settings.save()
