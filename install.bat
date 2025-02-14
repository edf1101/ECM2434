@echo off
pip install -r requirements.txt
cd eco_project || exit /B 1
python manage.py migrate
python manage.py clear_feature_data
python manage.py import_features
python manage.py clear_map_data
python manage.py import_map
python manage.py clear_badge_data
python manage.py import_badges
pause
