# Setting up the locations app

The locations app requires the database to be set up with the proper info
otherwise sites may not load or the map won't have any chunks to render. To simply this there are
tools to set up the database for you.

Firstly clear the location database by running the following commands (from the root of project):

```bash
python manage.py clear_feature_data
python manage.py clear_map_data
```

Then run the following command to set up the database with the proper info:

```bash
python manage.py import_features
python manage.py import_map
```