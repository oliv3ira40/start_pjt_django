"""Custom AdminSite implementation with configurable menu."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass

from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.urls import NoReverseMatch, reverse
from django.utils.text import slugify

from .models import MenuConfig, MenuItem

logger = logging.getLogger(__name__)


@dataclass
class _MenuEntry:
    app_key: str
    app_label: str
    app_name: str
    group_icon: str
    model_dict: dict[str, object]


class ColmeiaAdminSite(AdminSite):
    """Admin site that keeps the default behaviour with a configurable menu."""

    def get_app_list(self, request, app_label=None):
        base_app_list = list(super().get_app_list(request, app_label=app_label))

        if app_label is not None:
            return base_app_list

        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            return base_app_list
        if user.is_superuser:
            return base_app_list

        configured_menu = self.get_configured_menu(request)
        return configured_menu if configured_menu is not None else base_app_list

    def get_configured_menu(self, request) -> list[dict[str, object]] | None:
        """Build the menu backed by ``MenuConfig`` for the current request.

        ``None`` means that the established Django Admin fallback must be used;
        an empty list means a valid active configuration without visible items.
        """
        cached_menu = getattr(request, "_colmeia_configured_menu", ...)
        if cached_menu is not ...:
            return cached_menu

        user = getattr(request, "user", None)
        if not user or user.is_anonymous or user.is_superuser:
            request._colmeia_configured_menu = None
            return None

        try:
            config = (
                MenuConfig.objects.prefetch_related("items")
                .filter(scope=MenuConfig.Scope.NON_SUPERUSER, active=True)
                .order_by("-updated_at")
                .first()
            )
        except Exception:  # pragma: no cover - defensive fallback
            logger.exception("Unable to load menu configuration; falling back to default menu.")
            config = None

        if config:
            builder = _MenuBuilder(self, request, config)
            try:
                request._colmeia_configured_menu = builder.build()
            except Exception:  # pragma: no cover - defensive fallback
                logger.exception("Error while building custom admin menu; falling back to default menu.")
                request._colmeia_configured_menu = None
        else:
            request._colmeia_configured_menu = None

        return request._colmeia_configured_menu


class _MenuBuilder:
    """Helper responsible for converting MenuConfig entries to admin app_list."""

    def __init__(self, site: ColmeiaAdminSite, request, config: MenuConfig) -> None:
        self.site = site
        self.request = request
        self.config = config

    def build(self) -> list[dict[str, object]]:
        items = self.config.items.all().order_by("order", "id")
        grouped: OrderedDict[str, dict[str, object]] = OrderedDict()
        stats = {"ok": 0, "hidden_permission": 0, "hidden_reverse": 0, "hidden_other": 0}
        
        for item in items:
            entry, reason = self._build_entry(item)
            if entry is None:
                if reason == "permission":
                    stats["hidden_permission"] += 1
                elif reason == "reverse":
                    stats["hidden_reverse"] += 1
                else:
                    stats["hidden_other"] += 1
                continue
            
            stats["ok"] += 1
            app_dict = grouped.setdefault(
                entry.app_key,
                {
                    "app_label": entry.app_label,
                    "name": entry.app_name,
                    "menu_icon": entry.group_icon,
                    "app_url": "#",
                    "has_module_perms": True,
                    "models": [],
                },
            )
            app_dict["models"].append(entry.model_dict)

        # Log resumo
        total = sum(stats.values())
        if total > 0:
            logger.info(
                f"Menu '{self.config}' ({self.config.scope}): "
                f"{stats['ok']} itens ok, {stats['hidden_permission']} ocultados por permissão, "
                f"{stats['hidden_reverse']} com erro de reverse, {stats['hidden_other']} outros"
            )

        # Retornar lista vazia se necessário, mas nunca None (menu personalizado permanece ativo)
        return list(grouped.values())

    # === Builders ===
    def _build_entry(self, item: MenuItem) -> tuple[_MenuEntry | None, str]:
        """Retorna (entry, reason) onde reason explica por que foi ocultado se None."""
        if item.item_type == MenuItem.ItemType.MODEL:
            return self._build_model_entry(item)
        if item.item_type == MenuItem.ItemType.URL:
            return self._build_link_entry(item)
        return None, "invalid_type"

    def _build_model_entry(self, item: MenuItem) -> tuple[_MenuEntry | None, str]:
        model = item.get_model()
        if model is None:
            logger.warning(f"MenuItem {item.id}: modelo não encontrado ({item.app_label}.{item.model_name})")
            return None, "model_not_found"
        if model not in self.site._registry:
            logger.warning(f"MenuItem {item.id}: modelo {model.__name__} não registrado no admin")
            return None, "model_not_registered"

        model_admin = self.site._registry[model]
        perms = model_admin.get_model_perms(self.request)
        if not any(perms.values()):
            logger.debug(f"MenuItem {item.id}: usuário sem permissões para {model.__name__}")
            return None, "permission"

        model_meta = model._meta
        label = item.label or model_meta.verbose_name_plural.title()
        changelist_url = self._reverse_or_none(
            f"admin:{model_meta.app_label}_{model_meta.model_name}_changelist"
        )
        if changelist_url is None:
            logger.warning(f"MenuItem {item.id}: não foi possível fazer reverse de changelist para {model.__name__}")
            return None, "reverse"
        add_url = None
        if perms.get("add"):
            add_url = self._reverse_or_none(
                f"admin:{model_meta.app_label}_{model_meta.model_name}_add"
            )

        app_config = model_meta.app_config
        explicit_group = item.group_label.strip()
        if explicit_group:
            group_name = explicit_group
            app_key = slugify(group_name) or app_config.label
        else:
            # An ungrouped item must not collide with an explicit group whose
            # label happens to equal the app's verbose name (e.g. apiary).
            group_name = label
            app_key = f"item-{app_config.label}-{model_meta.model_name}"
        model_dict = {
            "name": label,
            "object_name": model_meta.object_name,
            "menu_icon": self._model_menu_icon(model_meta.app_label, model_meta.model_name),
            "active_view_prefix": f"admin:{model_meta.app_label}_{model_meta.model_name}_",
            "perms": perms,
            "admin_url": changelist_url,
            "add_url": add_url,
            "view_only": not perms.get("change", False),
        }
        return _MenuEntry(
            app_key=app_key,
            app_label=app_config.label,
            app_name=group_name,
            group_icon=self._group_menu_icon(item, default="hive"),
            model_dict=model_dict,
        ), "ok"

    def _build_link_entry(self, item: MenuItem) -> tuple[_MenuEntry | None, str]:
        # Resolver URL
        url = None
        if item.url_name:
            url = self._reverse_or_none(item.url_name)
            if url is None:
                logger.warning(
                    f"MenuItem {item.id}: não foi possível fazer reverse de '{item.url_name}'. "
                    f"Verifique se o nome está correto. Use namespace completo (ex.: admin:index) se necessário."
                )
        if not url and item.absolute_url:
            url = item.absolute_url
        if not url:
            return None, "reverse"

        # Checagem de permissão baseada em route_scope
        # route_scope='admin': exigir is_staff e permissões do admin
        # route_scope='site': não aplicar checagem de permissão do admin (a view controla)
        if item.route_scope == MenuItem.RouteScope.ADMIN:
            if not self.request.user.is_staff:
                logger.debug(f"MenuItem {item.id}: link admin requer is_staff")
                return None, "permission"
        
        # Permissão extra (se configurada, vale para qualquer tipo de link)
        permission_codename = item.permission_codename.strip()
        if permission_codename and not self.request.user.has_perm(permission_codename):
            logger.debug(f"MenuItem {item.id}: usuário sem permissão '{permission_codename}'")
            return None, "permission"

        label = item.label or item.url_name or item.absolute_url
        group_name = item.group_label.strip() if item.group_label else "Links"
        app_key = slugify(group_name) or "links"
        model_dict = {
            "name": label,
            "object_name": "CustomLink",
            "menu_icon": self._url_menu_icon(item.url_name),
            "active_view_name": item.url_name,
            "perms": {"add": False, "change": False, "delete": False, "view": True},
            "admin_url": url,
            "view_only": True,
        }
        return _MenuEntry(
            app_key=app_key,
            app_label=app_key,
            app_name=group_name,
            group_icon=self._group_menu_icon(item, default="folder"),
            model_dict=model_dict,
        ), "ok"

    @staticmethod
    def _model_menu_icon(app_label: str, model_name: str) -> str:
        """Return a presentation icon from stable model identifiers."""

        return {
            ("accounts", "person"): "user",
            ("apiary", "creatornetworkentry"): "map-pin",
            ("apiary", "apiary"): "apiary",
            ("apiary", "hive"): "hive",
            ("apiary", "externalmanagement"): "tools",
            ("apiary", "revision"): "clipboard",
        }.get((app_label, model_name), "folder")

    @staticmethod
    def _url_menu_icon(url_name: str) -> str:
        return {
            "admin:apiary_revision_sequence": "clipboard",
            "production-dashboard": "chart",
            "hive-history": "history",
            "hive-gallery": "image",
        }.get(url_name, "link")

    @staticmethod
    def _group_menu_icon(item: MenuItem, *, default: str) -> str:
        """Choose a group icon from its stable configured target, not its label."""

        if item.item_type == MenuItem.ItemType.MODEL:
            if item.app_label == "accounts":
                return "user"
            if item.app_label == "apiary":
                return "apiary"
        if item.url_name == "admin:apiary_revision_sequence":
            return "apiary"
        return default

    # === Helpers ===
    def _reverse_or_none(self, name: str) -> str | None:
        """Tenta fazer reverse da URL. Retorna None se falhar."""
        try:
            return reverse(name)
        except NoReverseMatch:
            return None
        except PermissionDenied:
            return None
        except Exception as e:
            logger.warning(f"Erro inesperado ao fazer reverse de '{name}': {e}")
            return None
