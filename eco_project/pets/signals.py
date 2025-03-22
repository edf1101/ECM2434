"""
Signals for the pets app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from pets.models import Pet

#pylint: disable=unused-argument
@receiver(post_save, sender=Pet)
def notify_low_health(sender, instance:Pet, **kwargs) -> None:
    """
    Sends an email to the pet's owner if the pet's health drops below 25%.

    @param sender: The sender of the signal
    @param instance: The instance of the model that was saved
    @param kwargs: The keyword arguments passed to the signal
    @return: None
    """

    # If the pet's health is below 25 and an email hasn't been sent yet:
    if instance.health < 25 and not instance.low_health_notified:
        subject = "Your pet needs help!"
        message = (
            f"Hi {instance.owner.username},\n\n"
            f"Your pet {instance.name}'s health has dropped below 25%. "
            "Please come back and take care of your pet before it's too late!"
        )
        recipient_list = [instance.owner.email]
        send_mail(subject, message, None, recipient_list, fail_silently=False)
        # Mark that we've sent the notification
        instance.low_health_notified = True
        instance.save(update_fields=["low_health_notified"])

    # If the pet's health has recovered to 25% or above and a notification was previously sent,
    # reset the flag.
    elif instance.health >= 25 and instance.low_health_notified:
        instance.low_health_notified = False
        instance.save(update_fields=["low_health_notified"])
