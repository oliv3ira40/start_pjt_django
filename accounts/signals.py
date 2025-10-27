from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Person

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_person_exists(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
        )
        return

    Person.objects.get_or_create(
        user=instance,
        defaults={
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
        },
    )
