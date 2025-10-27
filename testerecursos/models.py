from django.db import models


class ThreeResources(models.Model):
    class YesNoChoices(models.TextChoices):
        SIM = "sim", "Sim"
        NAO = "nao", "Não"

    class OptionChoices(models.TextChoices):
        A = "a", "Opção A"
        B = "b", "Opção B"
        C = "c", "Opção C"
        D = "d", "Opção D"
        E = "e", "Opção E"

    photo = models.ImageField("Foto", upload_to="testerecursos/photos/")
    yes_no = models.CharField(
        "Sim ou não",
        max_length=3,
        choices=YesNoChoices.choices,
    )
    description = models.TextField("Descrição", blank=True)
    option = models.CharField(
        "Opções",
        max_length=1,
        choices=OptionChoices.choices,
    )

    class Meta:
        verbose_name = "3 recursos"
        verbose_name_plural = "3 recursos"

    def __str__(self) -> str:
        return f"Recurso #{self.pk}" if self.pk else "Novo recurso"
