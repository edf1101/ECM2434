"""
This module contains the spinning wheel logic for the lootboxes app
"""
from users.models import User

WHEEL_OPTIONS = ['5 PetBucks', '10 Points', '5 Points', "25 Points",
                 "30 PetBucks", "40 PetBucks", "50 Points"]
OPTION_PROBABILITIES = [2, 1, 1.5, 0.4, 0.4, 0.2, 0.2]
OPTION_PROBABILITIES = [p / sum(OPTION_PROBABILITIES) for p in OPTION_PROBABILITIES]


def handle_result(result: str, user: User) -> None:
    """
    This function handles the result of the spinning wheel ie adding points etc to users

    @param result: the result of the spinning wheel
    @param user: the user to add the result to
    @return: None
    """

    if result == '5 PetBucks':
        user.profile.pet_bucks += 5
    elif result == '10 Points':
        user.profile.points += 10
    elif result == '5 Points':
        user.profile.points += 5
    elif result == '25 Points':
        user.profile.points += 25
    elif result == '30 PetBucks':
        user.profile.pet_bucks += 30
    elif result == '40 PetBucks':
        user.profile.pet_bucks += 40
    elif result == '50 Points':
        user.profile.points += 50

    user.profile.save()
