"""
This file is used to configure the challenges app
mainly just schedule the update_challenges task to run every 60 seconds.
"""
import atexit
import os

from django.apps import AppConfig

from .scheduler import scheduler


class ChallengesConfig(AppConfig):
    """
    Configuration class for the challenges app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "challenges"

    def ready(self):
        """
        This method is called when the app is ready to be used
        """

        # Skip scheduling if its just a reload of the server.
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .tasks import update_challenges
        import challenges.signals

        # Schedule the job for a 1m interval
        scheduler.add_job(
            update_challenges,
            'interval',
            seconds=60,
            id='update_challenges_job',
            replace_existing=True
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
