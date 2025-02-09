# Command Explaination

## import_chunks.py
This script is used to import 3D map chunk data into the database.
It would be a long manual process to import all ~400 chunks into the database so this script
automates it. There must be the console_out.txt file from blender in the same directory as this
script and the exports folder with all the .glb files in the same directory as this script.
```shell
python manage.py import_chunks
```

## clear_chunk_data.py
This script is used to clear all the chunk data from the database. This is useful for testing or 
just to clear the database of all chunk data.
```shell
python manage.py clear_chunk_data
```