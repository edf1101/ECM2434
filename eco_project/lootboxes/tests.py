"""
This module contains the tests for the lootboxes app.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""

import random
from django.test import TestCase
from django.contrib.auth import get_user_model
from lootboxes.models import LootBox
from unittest.mock import patch

User = get_user_model()

class LootBoxTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.profile.pet_bucks = 10  # Set initial pet bucks
        self.user.profile.points = 0  # Set initial points
        self.user.profile.save()
        self.lootbox = LootBox.objects.create(user=self.user)

    def test_spin_not_enough_pet_bucks(self):
        self.user.profile.pet_bucks = 4  # Not enough for a spin
        self.user.profile.save()
        with self.assertRaises(ValueError):
            self.lootbox.spin()

    @patch("random.choices", return_value=["winbig"])
    @patch("random.randint", return_value=30)
    def test_spin_winbig(self, mock_randint, mock_choices):
        result = self.lootbox.spin()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.pet_bucks, 5)  # 10 - 5 (cost of spin)
        self.assertEqual(self.user.profile.points, 30)  # Won 30 points
        self.assertIn("Congratulations! You won 30 points!", result)

    @patch("random.choices", return_value=["winsmall"])
    @patch("random.randint", return_value=5)
    def test_spin_winsmall(self, mock_randint, mock_choices):
        result = self.lootbox.spin()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.pet_bucks, 5)  # 10 - 5 (cost of spin)
        self.assertEqual(self.user.profile.points, 5)  # Won 5 points
        self.assertIn("Congratulations! You won 5 points!", result)

    @patch("random.choices", return_value=["winbucks"])
    @patch("random.randint", return_value=10)
    def test_spin_winbucks(self, mock_randint, mock_choices):
        result = self.lootbox.spin()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.pet_bucks, 15)  # 10 - 5 + 10 (won 10 bucks)
        self.assertIn("Congratulations! You won 5 bucks!", result)

    @patch("random.choices", return_value=["lose"])
    def test_spin_lose(self, mock_choices):
        result = self.lootbox.spin()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.pet_bucks, 5)  # 10 - 5 (cost of spin)
        self.assertIn("Sorry! You lost!", result)

    def test_lootbox_str(self):
        self.assertEqual(self.lootbox.__str__(), f"LootBox for {self.user.username}")
