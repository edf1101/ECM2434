# Ecopet - ECM2434

_EcoPet was made to raise awareness of sustainability challenges on campus aswell as encouraging eco
friendly behaviour by engaging with an endangered pet_

<img src="eco_project/static/media/readme_banner.png" alt="Alt Text" width="2568">


Group Members

- Hugo Blanco
- Ryan Butler
- Elizabeth Zara Brown
- Edward Fillingham
- Kit Matthewson
- Tasbir Rahaman
- Haruka Kimura

## Overview

### Details

Users can register a profile on Ecopet and their account detials are stored with compliance to GDPR
regulations.
Once an account is made users are able to create a pet which they can then care for by completing
eco friendly location based challenges or quizzes around campus to promote sustainability. Once your at a location for a
challenge you need to scan a QR code so that our GPS tracker can check that you are actually at the
location of the challenge.

Users can then check out our leaderboard page to compare how they are doing in terms of completing
challenges compared to the rest of the community.

### Engagement Features
We utilised gamification to make the app more engaging for users, this took the form of accessories
that you can buy for your pet, spinning wheels and animated components of the website.

We also added social features such as a friends list, a group system and 24h 'stories' with your pet.
We hope these features help keep users on the app and engaged with the sustainability challenges.

### Key Project Features

- 3D map to show the location of challenges around the map
- Fully responsive design for mobile and desktop users
- Dynamic leaderboard with multiple filter options
- 24h lasting stories as a social aspect of the app

## Usage & Installation

### Installation from source
To install from source yourself, clone the repository and run the install script.

```shell
Assuming you have a virtual environment set up:

```shell
chmod 755 install.sh
./install.sh
```

(Windows)

```shell
.\install.bat
```
To then run the code from the base ECM2434 folder go to the eco_project folder
```shell
cd eco_project
```
You can then run the server
```shell
python manage.py runserver
```

### Regular Usage

For normal users you can access the website by going to the hosted version at [this link.](https://edfillingham1.pythonanywhere.com)


## Code Maintenance and Quality

### Linting
To run `pylint` on the project:

```shell
cd ECM2434
pylint eco_project
```

## Testing & Coverage Reports
To install coverage:
```shell
pip install coverage
```

To generate a full test coverage report:

```shell
coverage run manage.py test
coverage report -m
```

To generate a report for a specific app:

```shell
coverage run manage.py test [app_name]
coverage report -m --include="*/[app_name]/*"
```

## GDPR Compliance

This project complies with the GDPR - see [GDPR](GDPR.md) for details.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
