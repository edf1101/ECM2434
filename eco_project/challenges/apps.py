"""
This file is used to configure the challenges app
mainly just schedule the update_challenges task to run every 60 seconds.

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import atexit
import os

from django.apps import AppConfig

from .scheduler import scheduler


# pylint errors are wrong here, the import is needed in the ready method
# pylint: disable=unused-import, import-outside-toplevel,W0108

class ChallengesConfig(AppConfig):
    """
    Configuration class for the challenges app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "challenges"

    def ready(self) -> None:
        """
        This method is called when the app is ready to be used
        """

        # Skip scheduling if its just a reload of the server.
        if os.environ.get("RUN_MAIN") != "true":
            return

        from .tasks import update_challenges,update_pet_health

        # Schedule the job for a 1m interval
        scheduler.add_job(
            update_challenges,
            "interval",
            seconds=60,
            id="update_challenges_job",
            replace_existing=True,
        )

          # Schedule the pet health update job to run every 24 hours.
        scheduler.add_job(
            update_pet_health,
            "interval",
            seconds=86400,  
            id="update_pet_health_job",
            replace_existing=True,
        )
        
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
