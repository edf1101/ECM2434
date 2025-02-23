import os
from django.core.management.base import BaseCommand
from users.models import Badge  # Adjust the import if your Badge model is in a different module


class Command(BaseCommand):
    """
    This script imports badge data from a file into the database.
    The expected format for each non-comment line in badge_data.txt is:

        Badge title, Badge description, Badge colour as #HEX, Badge rarity

    Example line:
        100 Day Streak, You've logged in for 100 days in a row!, #d4b86c, 10
    """
    help = "Import badge data into the database from badge_data.txt"

    def handle(self, *args, **kwargs) -> None:
        """
               Reads badge data from badge_data.txt and creates Badge objects.
               """
        file_path = os.path.join(os.getcwd(), "users/management/commands/badge_data.txt")

        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
        except FileNotFoundError:  # Throw error if file not found
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        # Remove blank lines and comments
        lines = [line.strip() for line in lines if
                 line.strip() and not line.strip().startswith("#")]

        successes = 0
        for line in lines:
            fields = [field.strip() for field in line.split(",")]
            if len(fields) != 4:  # Throw error if line does not have 4 fields
                self.stdout.write(self.style.ERROR(f"Invalid format in line: {line}"))
                continue

            title, hover_text, colour, rarity_str = fields

            try:
                rarity = int(rarity_str)
            except ValueError:  # Throw error if rarity is not an integer
                self.stdout.write(
                    self.style.ERROR(f"Invalid rarity value '{rarity_str}' in line: {line}"))
                continue
            # Make Badge
            badge = Badge(title=title, hover_text=hover_text, colour=colour, rarity=rarity)
            try:
                badge.save()
                successes += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error saving badge '{title}': {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"Saved {successes} badge(s) to the database"))
