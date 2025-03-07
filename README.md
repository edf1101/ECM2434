# Ecopet - ECM2434

Sustainability Group Software Engineering Project by Team Group

<img src="eco_project/static/media/readme_banner.png" alt="Alt Text" width="1000">


Group Members

- Hugo Blanco
- Ryan Butler
- Elizabeth Zara Brown
- Edward Fillingham
- Kit Matthewson
- Tasbir Rahaman
- Haruka Kimura

# Project Overview

EcoPet was made to raise awareness of sustainability challenges on campus aswell as encouraging eco
friendly behaviour by engaging with an endangered pet

# Details

Users can register a profile on Ecopet and their account detials are stored with compliance to GDPR
regulations.
Once an account is made users are able to create a pet which they can then care for by completing
eco freindly challenges around campus to promote sustainability. Once your at a location for a
challenge you need to scan a QR code so that our GPS tracker can check that you are actually at the
location of the challenge.
Users can then check out our leaderboard page to compare how they are doing in terms of completing
chanllenges compared to the rest of the community.

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
cd ECM2434
pylint eco_project
```

To generate a test coverage report:

```shell
pip install coverage
cd eco_project
coverage run --source='.' manage.py test mysite
coverage report
```

## GDPR Compliance

This project complies with the GDPR - see [GDPR](GDPR.md) for details.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
