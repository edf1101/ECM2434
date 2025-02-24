@echo off
pip install -r requirements.txt -q
cd eco_project || exit /B 1
python manage.py flush --no-input
python manage.py migrate
python manage.py clear_feature_data
python manage.py import_features
python manage.py clear_map_data
python manage.py import_map
python manage.py clear_badge_data
python manage.py import_badges
python manage.py create_pets
python manage.py create_gamekeeper_group
pause
