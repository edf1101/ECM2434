# Ecopet - ECM2434
Sustainability Group Software Engineering Project 

Group Members
- Hugo Blanco
- Ryan Butler
- Elizabeth Zara Brown
- Edward Fillingham
- Kit Matthewson
- Tasbir Rahaman
- Haruka Kimura

# Project Overview 
EcoPet was made to raise awareness of sustainability challenges on campus aswell as encouraging eco freinldy behaviour by engaging with an endangered pet 

# Details 
Users can register a profile on Ecopet and thier account detials are stored with compliance to GDPR regulations.
Once an account is made users are able to create a pet which they can then care for by completing eco freindly challenges around campus to promote sustainability. 
Users can then check out our leaderboard page to compare how they are doing in terms of completing chanllenges compared to teh rest of the community. 

## Installing
Assuming you have a virtual environment set up (We will containerise later before submission?)
(macos/linux)
```shell
chmod 755 install.sh
./install.sh
```
(windows)
```shell
.\install.bat
```

## How to run After Installation
From the base ECM2434 folder go to the eco_project folder 
```shell
cd eco_project
```

You can then run the manage.py commands eg:
```shell
python manage.py runserver
```

To run pylint on the project:
```shell
pylint .
```

To generate a test coverage report:
```shell
pip install coverage
cd eco_project
coverage run --source='.' manage.py test mysite
coverage report
```
