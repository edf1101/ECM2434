"""
This module contains the models needed for the lootboxes app

@author: 730022096
"""

import random
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LootBox(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lootbox")

    def spin(self):
        """Simulate spinning the lootbox wheel"""
        profile = self.user.profile

        if profile.pet_bucks < 5:
            raise ValueError("Not enough pet bucks to spin.")

        # Deduct points for spinning
        profile.pet_bucks -= 5

        # Define possible outcomes and their probabilities
        outcomes = ["winbig", "winsmall", "lose", "winbucks"]
        probabilities = [0.1, 0.325, 0.25, 0.325]

        # Spin the wheel and choose an outcome based on the specified probabilities
        outcome = random.choices(outcomes, weights=probabilities, k=1)[0]

        if outcome == "winbig":
            # Win between 10 and 50 points
            winnings = random.randint(10, 50)
            profile.points += winnings
            result = f"Congratulations! You won {winnings} points! Total points: {profile.points}, Total Bucks: {profile.pet_bucks}"
        elif outcome == "winsmall":
            # Win between 1 and 10 points
            winnings = random.randint(1, 10)
            profile.points += winnings
            result = f"Congratulations! You won {winnings} points! Total points: {profile.points} Total Bucks: {profile.pet_bucks}"
        elif outcome == "winbucks":
            # Win between 1 and 10 bucks
            winnings = random.randint(6, 15)
            profile.pet_bucks += winnings
            result = f"Congratulations! You won {winnings-5} bucks! Total points: {profile.points} Total Bucks: {profile.pet_bucks}"
        elif outcome == "lose":
            # Lose some bucks
            result = f"Sorry! You lost! Total Bucks: {profile.pet_bucks}"

        # Save the profile after modifying the points
        profile.save()

        return result

    def __str__(self):
        return f"LootBox for {self.user.username}"
