from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Person


class Command(BaseCommand):
    help = "Cria registros Person ausentes copiando dados dos usuários existentes."

    def handle(self, *args, **options):
        User = get_user_model()
        created = 0

        for user in User.objects.all():
            person, was_created = Person.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                },
            )
            if was_created:
                created += 1

        if created:
            self.stdout.write(self.style.SUCCESS(f"{created} registro(s) Person criado(s)."))
        else:
            self.stdout.write(self.style.SUCCESS("Nenhum Person precisava ser criado."))
