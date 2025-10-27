from __future__ import annotations

from typing import Iterable, Optional

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class MenuScopeQuerySet(models.QuerySet):
    def ordered(self) -> "MenuScopeQuerySet":
        return self.order_by("-priority", "name", "pk")

    def for_groups(self, group_ids: Iterable[int]) -> "MenuScopeQuerySet":
        return self.filter(group_id__in=list(group_ids))

    def default_scope(self) -> "MenuScopeQuerySet":
        return self.filter(group__isnull=True)


class MenuConfigQuerySet(models.QuerySet):
    def active(self) -> "MenuConfigQuerySet":
        return self.filter(is_active=True)

    def for_scope(self, scope: "MenuScope") -> "MenuConfigQuerySet":
        return self.filter(scope=scope)


class MenuScope(models.Model):
    name = models.CharField(_("Nome"), max_length=150)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="admin_menu_scope",
        verbose_name=_("Grupo"),
    )
    priority = models.IntegerField(
        _("Prioridade"),
        default=0,
        help_text=_(
            "Escopos com prioridade maior são escolhidos primeiro quando o usuário"
            " pertence a vários grupos."
        ),
    )

    objects = MenuScopeQuerySet.as_manager()

    class Meta:
        verbose_name = _("Escopo")
        verbose_name_plural = _("Escopos")
        ordering = ("-priority", "name", "pk")

    def __str__(self) -> str:
        if self.group:
            return f"{self.name} ({self.group.name})"
        return f"{self.name}"

    def clean(self) -> None:
        super().clean()
        if (
            self.group is None
            and MenuScope.objects.default_scope().exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                {"group": _("Já existe um escopo padrão sem grupo associado.")}
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class MenuConfig(models.Model):
    scope = models.ForeignKey(
        MenuScope,
        on_delete=models.CASCADE,
        related_name="menu_configs",
        verbose_name=_("Escopo"),
    )
    is_active = models.BooleanField(
        _("Ativa"),
        default=False,
        help_text=_("Marque para tornar essa configuração a vigente para o escopo."),
    )
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    objects = MenuConfigQuerySet.as_manager()

    class Meta:
        verbose_name = _("Configuração de menu")
        verbose_name_plural = _("Configurações de menu")
        ordering = ("scope__priority", "scope__name", "-is_active", "pk")
        constraints = (
            models.UniqueConstraint(
                fields=("scope",),
                condition=Q(is_active=True),
                name="unique_active_menu_per_scope",
            ),
        )

    def __str__(self) -> str:
        status = _("ativa") if self.is_active else _("inativa")
        return f"{self.scope} ({status})"

    @classmethod
    def get_active_for_scope(cls, scope: Optional[MenuScope]) -> Optional["MenuConfig"]:
        if scope is None:
            return None

        return (
            cls.objects.for_scope(scope)
            .active()
            .order_by("-updated_at", "-pk")
            .prefetch_related(
                models.Prefetch(
                    "items",
                    queryset=MenuItem.objects.order_by("order", "pk"),
                )
            )
            .first()
        )

    def ordered_items(self) -> Iterable["MenuItem"]:
        cache = getattr(self, "_prefetched_objects_cache", {})
        if "items" in cache:
            return sorted(cache["items"], key=lambda item: (item.order, item.pk))
        return self.items.order_by("order", "pk")

    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.is_active:
                (
                    self.__class__.objects.filter(scope=self.scope)
                    .exclude(pk=self.pk)
                    .update(is_active=False)
                )


class MenuItem(models.Model):
    class ItemType(models.TextChoices):
        MODEL = "model", _("Modelo")
        URL = "url", _("Link personalizado")

    config = models.ForeignKey(
        MenuConfig,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Configuração"),
    )
    order = models.PositiveIntegerField(_("Ordem"), default=0)
    item_type = models.CharField(
        _("Tipo"), max_length=16, choices=ItemType.choices, default=ItemType.MODEL
    )
    section = models.CharField(
        _("Seção"),
        max_length=150,
        blank=True,
        help_text=_(
            "Nome do grupo em que o item será exibido. Deixe em branco para usar o nome do app."
        ),
    )
    label = models.CharField(
        _("Rótulo"),
        max_length=150,
        blank=True,
        help_text=_("Texto exibido no menu. Deixe vazio para usar o padrão."),
    )
    app_label = models.CharField(
        _("App"),
        max_length=100,
        blank=True,
        help_text=_("Utilize apenas para itens do tipo modelo."),
    )
    model_name = models.CharField(
        _("Modelo"),
        max_length=100,
        blank=True,
        help_text=_("Nome do modelo em letras minúsculas (ex.: especie)."),
    )
    url_name = models.CharField(
        _("Nome da URL"),
        max_length=200,
        blank=True,
        help_text=_("reverse() será aplicado. Informe namespaces se necessário."),
    )
    absolute_url = models.URLField(
        _("URL absoluta"),
        blank=True,
        help_text=_("Utilizado como fallback quando a URL nomeada não for encontrada."),
    )
    permission_codename = models.CharField(
        _("Permissão extra"),
        max_length=150,
        blank=True,
        help_text=_("Opcional. Utilize o formato app_label.codename."),
    )

    class Meta:
        verbose_name = _("Item de menu")
        verbose_name_plural = _("Itens de menu")
        ordering = ("order", "pk")

    def __str__(self) -> str:
        target = self.label or self.model_name or self.url_name or self.absolute_url
        return f"{self.get_item_type_display()} - {target}" if target else self.get_item_type_display()

    def clean(self) -> None:
        super().clean()
        if self.item_type == self.ItemType.MODEL:
            if not self.app_label or not self.model_name:
                raise ValidationError(
                    {"app_label": _("Informe o app."), "model_name": _("Informe o modelo.")}
                )
        if self.item_type == self.ItemType.URL and not (self.url_name or self.absolute_url):
            raise ValidationError(
                {
                    "url_name": _("Informe o nome da URL."),
                    "absolute_url": _("ou uma URL absoluta."),
                }
            )

    def save(self, *args, **kwargs) -> None:
        if self.app_label:
            self.app_label = self.app_label.strip().lower()
        if self.model_name:
            self.model_name = self.model_name.strip().lower()
        if self.label:
            self.label = self.label.strip()
        if self.section:
            self.section = self.section.strip()
        if self.permission_codename:
            self.permission_codename = self.permission_codename.strip()
        if self.url_name:
            self.url_name = self.url_name.strip()
        if self.absolute_url:
            self.absolute_url = self.absolute_url.strip()
        super().save(*args, **kwargs)

    def has_additional_permission(self, user) -> bool:
        if not self.permission_codename:
            return True
        return user.has_perm(self.permission_codename)

    def display_label(self) -> str:
        return self.label.strip() if self.label else ""

    def section_name(self) -> str:
        return self.section.strip() if self.section else ""
