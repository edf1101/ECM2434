pip install -r requirements.txt
cd eco_project || exit
rm db.sqlite3
python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py clear_feature_data
python manage.py import_features
python manage.py clear_map_data
python manage.py import_map
python manage.py clear_badge_data
python manage.py import_badges
