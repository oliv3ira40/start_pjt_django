from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        verbose_name="Primeiro nome",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        verbose_name="Último nome",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        verbose_name="E-mail",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="person",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pessoa",
                "verbose_name_plural": "Pessoas",
            },
        ),
    ]
