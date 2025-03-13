"""
This file is used to configure the petReal app. It is used to schedule the removal of expired photos
and import signals
"""
import atexit
import os

from django.apps import AppConfig
from mysite.scheduler import scheduler
from apscheduler.schedulers.base import SchedulerAlreadyRunningError


class PetrealConfig(AppConfig):
    """
    This class is used to configure the petReal app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "petreal"

    def ready(self) -> None:
        # Prevent scheduling on autoreload
        if os.environ.get("RUN_MAIN") != "true":
            return

        # pylint: disable=import-outside-toplevel,unused-import
        from .tasks import remove_expired_photos
        from .signals import delete_user_photo_file

        scheduler.add_job(
            remove_expired_photos,
            "interval",
            seconds=60,
            id="remove_expired_photos_job",
            replace_existing=True,
        )

        # make sure the scheduler shuts down when Django stops
        try:
            scheduler.start()
        except SchedulerAlreadyRunningError:
            pass
        atexit.register(scheduler.shutdown)
