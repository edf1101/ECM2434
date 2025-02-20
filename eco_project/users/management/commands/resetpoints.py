from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Updates all user profile points based on their pets'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        updated = 0
        for user in users:
            user.profile.update_points()
            updated += 1
        self.stdout.write(f'Updated points for {updated} profiles')