from __future__ import annotations

import logging
from collections import OrderedDict
from copy import copy

from django.apps import apps
from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.urls import NoReverseMatch, reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CustomAdminSite(AdminSite):
    site_title = "Django admin"
    site_header = "Django admin"
    index_title = "Django admin"

    def get_app_list(self, request, app_label=None):
        default_list = super().get_app_list(request, app_label=app_label)
        if app_label or request.user.is_superuser:
            return default_list

        config = self._resolve_active_config(request.user)
        if not config:
            return default_list

        try:
            custom_list = self._build_custom_app_list(request, config)
        except Exception:  # pragma: no cover - defensive fallback
            logger.exception("Failed to build custom admin menu. Falling back to default list.")
            return default_list

        return custom_list or default_list

    def _resolve_active_config(self, user):
        menu_config_model = apps.get_model("admin_menu", "MenuConfig")
        menu_scope_model = apps.get_model("admin_menu", "MenuScope")

        if not user.is_authenticated:
            return menu_config_model.get_active_for_scope(
                menu_scope_model.objects.default_scope().ordered().first()
            )

        group_ids = list(user.groups.values_list("id", flat=True))
        if group_ids:
            scope = (
                menu_scope_model.objects.for_groups(group_ids)
                .ordered()
                .first()
            )
            config = menu_config_model.get_active_for_scope(scope)
            if config:
                return config

        default_scope = menu_scope_model.objects.default_scope().ordered().first()
        if default_scope:
            return menu_config_model.get_active_for_scope(default_scope)
        return None

    def _build_custom_app_list(self, request, config):
        app_dict = self._build_app_dict(request)
        sections: "OrderedDict[str, dict]" = OrderedDict()

        for item in config.ordered_items():
            if not item.has_additional_permission(request.user):
                continue

            if item.item_type == item.ItemType.MODEL:
                entry = self._build_model_entry(item, app_dict)
            else:
                entry = self._build_url_entry(item)

            if not entry:
                continue

            section_key, section_defaults, model_entry = entry
            section = sections.setdefault(section_key, section_defaults)
            section.setdefault("models", []).append(model_entry)

        return list(sections.values())

    def _build_model_entry(self, item: MenuItem, app_dict):
        app_label = item.app_label
        model_name = item.model_name
        if not app_label or not model_name:
            return None

        app_info = app_dict.get(app_label)
        if not app_info:
            return None

        model_entry = None
        for entry in app_info.get("models", []):
            model = entry.get("model")
            entry_model_name = getattr(model._meta, "model_name", None) if model else None
            if entry_model_name == model_name:
                model_entry = entry.copy()
                break

        if not model_entry:
            return None

        if item.display_label():
            model_entry["name"] = item.display_label()

        model_entry.pop("model", None)

        section_name = item.section_name() or app_info.get("name") or app_label
        section_key = f"app:{section_name}" if item.section_name() else f"app:{app_label}"

        if item.section_name():
            section_defaults = {
                "name": section_name,
                "app_label": slugify(section_name) or section_name,
                "app_url": "#",
                "has_module_perms": True,
                "models": [],
            }
        else:
            section_defaults = copy(app_info)
            section_defaults["models"] = []

        return section_key, section_defaults, model_entry

    def _build_url_entry(self, item: MenuItem):
        url = None
        if item.url_name:
            try:
                url = reverse(item.url_name)
            except NoReverseMatch:
                url = None
        if not url and item.absolute_url:
            url = item.absolute_url
        if not url:
            return None

        label = item.display_label() or item.url_name or item.absolute_url
        section_name = item.section_name() or _("Links")
        section_key = f"link:{section_name}"
        section_defaults = {
            "name": section_name,
            "app_label": slugify(section_name) or "links",
            "app_url": url if item.section_name() else "#",
            "has_module_perms": True,
            "models": [],
        }
        model_entry = {
            "name": label,
            "object_name": slugify(label) or label,
            "perms": {"add": False, "change": False, "delete": False, "view": True},
            "admin_url": url,
            "add_url": None,
            "view_only": True,
        }
        return section_key, section_defaults, model_entry


class CustomAdminConfig(AdminConfig):
    default_site = "core.admin_site.CustomAdminSite"
