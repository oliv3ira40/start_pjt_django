from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário"),
        related_name="person",
    )
    first_name = models.CharField(
        _("Primeiro nome"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("Último nome"),
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        _("E-mail"),
        blank=True,
    )
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Pessoa")
        verbose_name_plural = _("Pessoas")

    def __str__(self) -> str:
        return self.user.get_username()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        user = self.user
        fields_to_update = []

        if user.first_name != self.first_name:
            user.first_name = self.first_name
            fields_to_update.append("first_name")
        if user.last_name != self.last_name:
            user.last_name = self.last_name
            fields_to_update.append("last_name")
        if user.email != self.email:
            user.email = self.email
            fields_to_update.append("email")

        if fields_to_update:
            user.save(update_fields=fields_to_update)
