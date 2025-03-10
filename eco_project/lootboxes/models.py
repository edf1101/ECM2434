import random
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LootBox(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lootbox")

    def spin(self):
        """Simulate spinning the lootbox wheel"""
        profile = self.user.profile  # Access the user's profile to update their points

        if profile.points < 10:
            raise ValueError("Not enough points to spin.")

        # Deduct points for spinning
        profile.points -= 10

        # Define possible outcomes and their probabilities
        outcomes = ["winbig", "winsmall", "lose", "loseall"]
        probabilities = [0.2, 0.425, 0.325, 0.05]

        # Spin the wheel and choose an outcome based on the specified probabilities
        outcome = random.choices(outcomes, weights=probabilities, k=1)[0]

        if outcome == "winbig":
            # Win between 30 and 100 points
            winnings = random.randint(30, 100)
            profile.points += winnings
            result = f"Congratulations! You won {winnings} points! Total points: {profile.points}"
        elif outcome == "winsmall":  # Corrected here
            # Win between 10 and 30 points
            winnings = random.randint(10, 30)
            profile.points += winnings
            result = f"Congratulations! You won {winnings} points! Total points: {profile.points}"
        elif outcome == "lose":
            # Lose some points
            result = f"Sorry! You lost 10 points! Total points: {profile.points}"
        elif outcome == "loseall":
            # Lose all points
            profile.points = 0
            result = f"Sorry! You lost all your points! Total points: {profile.points}"

        # Save the profile after modifying the points
        profile.save()

        return result

    def __str__(self):
        return f"LootBox for {self.user.username}"
