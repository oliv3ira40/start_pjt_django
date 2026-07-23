"""Seed the navigation used by non-superusers in the Django admin."""

from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from admin_menu.models import MenuConfig, MenuItem


@dataclass(frozen=True)
class MenuEntry:
    """A stable definition for an item in the default admin navigation."""

    order: int
    group_label: str
    label: str
    item_type: str
    app_label: str = ""
    model_name: str = ""
    url_name: str = ""
    route_scope: str = MenuItem.RouteScope.ADMIN
    permission_codename: str = ""


APIARY_GROUP = "Meliponário"

MENU_ENTRIES = (
    MenuEntry(100, "", "Perfil", MenuItem.ItemType.MODEL, "accounts", "person"),
    MenuEntry(200, "", "Criadores por região", MenuItem.ItemType.MODEL, "apiary", "creatornetworkentry"),
    MenuEntry(201, APIARY_GROUP, "Revisão em sequência", MenuItem.ItemType.URL, url_name="admin:apiary_revision_sequence", permission_codename="apiary.add_revision"),
    MenuEntry(300, APIARY_GROUP, "Meus meliponários", MenuItem.ItemType.MODEL, "apiary", "apiary"),
    MenuEntry(400, APIARY_GROUP, "Colmeias", MenuItem.ItemType.MODEL, "apiary", "hive"),
    MenuEntry(500, APIARY_GROUP, "Manejos externos", MenuItem.ItemType.MODEL, "apiary", "externalmanagement"),
    MenuEntry(600, APIARY_GROUP, "Revisões", MenuItem.ItemType.MODEL, "apiary", "revision"),
    MenuEntry(700, APIARY_GROUP, "Dashboard de produção", MenuItem.ItemType.URL, url_name="production-dashboard"),
    MenuEntry(800, APIARY_GROUP, "Histórico da colmeia", MenuItem.ItemType.URL, url_name="hive-history"),
    MenuEntry(900, APIARY_GROUP, "Galeria de imagens", MenuItem.ItemType.URL, url_name="hive-gallery"),
)


class Command(BaseCommand):
    help = "Cria ou atualiza, de forma idempotente, o menu administrativo padrão."

    def handle(self, *args, **options):
        with transaction.atomic():
            config, created_config = self._get_config()
            removed = self._remove_deprecated_items(config)
            created = 0
            updated = 0

            for entry in MENU_ENTRIES:
                item, created_item = self._upsert_item(config, entry)
                created += created_item
                updated += not created_item
                self.stdout.write(
                    f"{'Criado' if created_item else 'Atualizado'}: {item.label}."
                )

            self._move_remaining_items_after_initial_navigation(config)

        config_action = "criada" if created_config else "reutilizada"
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed do menu concluída: configuração {config_action}, "
                f"{created} item(ns) criado(s), {updated} atualizado(s) e "
                f"{removed} item(ns) antigo(s) removido(s)."
            )
        )

    @staticmethod
    def _get_config() -> tuple[MenuConfig, bool]:
        config = (
            MenuConfig.objects.filter(scope=MenuConfig.Scope.NON_SUPERUSER, active=True)
            .order_by("-updated_at", "-pk")
            .first()
        )
        if config:
            return config, False

        config = (
            MenuConfig.objects.filter(scope=MenuConfig.Scope.NON_SUPERUSER)
            .order_by("-updated_at", "-pk")
            .first()
        )
        if config:
            return config, False

        return (
            MenuConfig.objects.create(
                scope=MenuConfig.Scope.NON_SUPERUSER,
                active=True,
            ),
            True,
        )

    @staticmethod
    def _remove_deprecated_items(config: MenuConfig) -> int:
        """Remove menu entries only; their domain records remain untouched."""

        deprecated = config.items.filter(
            Q(item_type=MenuItem.ItemType.MODEL, app_label="apiary", model_name="quickobservation")
            | Q(item_type=MenuItem.ItemType.MODEL, app_label="apiary", model_name="revisionattachment")
            | Q(item_type=MenuItem.ItemType.MODEL, app_label="apiary", model_name="hivelisting")
            | Q(item_type=MenuItem.ItemType.MODEL, app_label="apiary", model_name="hiveclaim")
            | Q(item_type=MenuItem.ItemType.MODEL, app_label="accounts", model_name="usersettings")
            | Q(item_type=MenuItem.ItemType.MODEL, app_label="flora")
            | Q(item_type=MenuItem.ItemType.URL, url_name__in={
                "plant-history",
                "plant-history-qr-code",
                "plant-revision-link-qr-code",
                "plant-history-export-pdf",
                "plant-history-public",
            })
            | Q(item_type=MenuItem.ItemType.URL, url_name="accounts:subscription_renewal")
            | Q(item_type=MenuItem.ItemType.URL, url_name="admin:my_referrals")
        )
        count = deprecated.count()
        deprecated.delete()
        return count

    @staticmethod
    def _upsert_item(config: MenuConfig, entry: MenuEntry) -> tuple[MenuItem, bool]:
        item = Command._find_existing_item(config, entry)
        created = item is None
        if item is None:
            item = MenuItem(config=config)

        # Preserve permission_codename, which can be intentionally more
        # restrictive in an existing installation.
        item.order = entry.order
        item.item_type = entry.item_type
        item.route_scope = entry.route_scope
        item.group_label = entry.group_label
        item.label = entry.label
        item.app_label = entry.app_label
        item.model_name = entry.model_name
        item.url_name = entry.url_name
        item.absolute_url = ""
        if entry.permission_codename and not item.permission_codename:
            item.permission_codename = entry.permission_codename
        item.save()
        return item, created

    @staticmethod
    def _find_existing_item(config: MenuConfig, entry: MenuEntry) -> MenuItem | None:
        if entry.item_type == MenuItem.ItemType.MODEL:
            item = config.items.filter(
                item_type=MenuItem.ItemType.MODEL,
                app_label=entry.app_label,
                model_name=entry.model_name,
            ).order_by("pk").first()
        else:
            item = config.items.filter(
                item_type=MenuItem.ItemType.URL,
                url_name=entry.url_name,
            ).order_by("pk").first()

        if item:
            return item

        # The current seed predates stable route/model identifiers in a few
        # installations. These labels are migration aliases, not new entries.
        legacy_labels = {
            "Dashboard de produção": "Produção",
            "Galeria de imagens": "Galeria da colmeia",
            "Criadores por região": "Criador por região",
        }
        return config.items.filter(label=legacy_labels.get(entry.label, entry.label)).order_by("pk").first()

    @staticmethod
    def _move_remaining_items_after_initial_navigation(config: MenuConfig) -> None:
        """Keep every unseeded entry after the requested initial navigation."""

        last_initial_order = MENU_ENTRIES[-1].order
        seeded_item_ids = [
            Command._find_existing_item(config, entry).pk for entry in MENU_ENTRIES
        ]
        remaining_items = (
            config.items.exclude(pk__in=seeded_item_ids)
            .order_by("order", "pk")
        )
        for index, item in enumerate(remaining_items, start=1):
            item.order = last_initial_order + index * 100
            item.save(update_fields=["order"])
