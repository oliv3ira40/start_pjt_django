"""Seed the official Colmeias Online django-admin-interface theme."""

from __future__ import annotations

import hashlib
from pathlib import Path

from admin_interface.models import Theme
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q


THEME_NAME = "colmeias-online"
IDENTITY_ROOT = (
    settings.BASE_DIR / "core" / "static" / "identidade-visual" / "assets"
)
LOGO_SOURCE = IDENTITY_ROOT / "logos" / "colmeias-online-logo-negativa-transparente.png"
FAVICON_SOURCE = IDENTITY_ROOT / "icones" / "favicon.ico"
LOGO_DESTINATION = "admin-interface/logo/colmeias-online-logo-negativa.png"
FAVICON_DESTINATION = "admin-interface/favicon/colmeias-online-favicon.ico"

# Only visual/branding fields belong to this seed. Interaction preferences from
# django-admin-interface deliberately remain under the administrator's control.
THEME_FIELDS = {
    "name": THEME_NAME,
    "active": True,
    "title": "Colmeias Online",
    "title_color": "#F6AF08",
    "title_visible": False,
    "logo_color": "#F8F7F1",
    "logo_max_width": 220,
    "logo_max_height": 64,
    "logo_visible": True,
    "env_visible_in_favicon": False,
    "css_header_background_color": "#0B2717",
    "css_header_text_color": "#F8F7F1",
    "css_header_link_color": "#F8F7F1",
    "css_header_link_hover_color": "#F6AF08",
    "css_module_background_color": "#193315",
    "css_module_background_selected_color": "#DCEBCF",
    "css_module_text_color": "#F8F7F1",
    "css_module_link_color": "#F8F7F1",
    "css_module_link_selected_color": "#193315",
    "css_module_link_hover_color": "#F6AF08",
    "css_generic_link_color": "#193315",
    "css_generic_link_hover_color": "#0B2717",
    "css_generic_link_active_color": "#78962C",
    "css_save_button_background_color": "#193315",
    "css_save_button_background_hover_color": "#0B2717",
    "css_save_button_text_color": "#F8F7F1",
}


class Command(BaseCommand):
    help = "Cria ou atualiza, de forma idempotente, o tema oficial do Admin."

    def handle(self, *args, **options):
        self._validate_sources()

        with transaction.atomic():
            theme = self._get_official_theme()
            old_logo = theme.logo.name if theme.pk else ""
            old_favicon = theme.favicon.name if theme.pk else ""

            for field, value in THEME_FIELDS.items():
                setattr(theme, field, value)

            theme.logo.name = _store_asset(LOGO_SOURCE, LOGO_DESTINATION)
            theme.favicon.name = _store_asset(FAVICON_SOURCE, FAVICON_DESTINATION)
            theme.save()

            _delete_if_unreferenced(old_logo, theme.pk)
            _delete_if_unreferenced(old_favicon, theme.pk)

        self.stdout.write(self.style.SUCCESS("Tema oficial do Colmeias Online atualizado."))

    @staticmethod
    def _validate_sources() -> None:
        for source in (LOGO_SOURCE, FAVICON_SOURCE):
            if not source.is_file():
                raise CommandError(
                    f"Ativo oficial da identidade visual não encontrado: {source}"
                )

    @staticmethod
    def _get_official_theme() -> Theme:
        theme = Theme.objects.filter(name=THEME_NAME).first()
        if theme:
            return theme

        # Installations before this seed used the sole active Theme created in
        # the admin. Reuse it once and give it the stable official key instead
        # of creating a parallel theme.
        theme = Theme.objects.filter(active=True).order_by("-pk").first()
        if theme:
            return theme

        theme = Theme.objects.order_by("pk").first()
        return theme or Theme()


def _store_asset(source: Path, destination: str) -> str:
    """Store a source asset once, replacing it only when its content changes."""

    if default_storage.exists(destination):
        with default_storage.open(destination, "rb") as stored, source.open("rb") as official:
            if _digest(stored) == _digest(official):
                return destination
        default_storage.delete(destination)

    with source.open("rb") as official:
        return default_storage.save(destination, File(official, name=source.name))


def _digest(file_object) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: file_object.read(64 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _delete_if_unreferenced(name: str, theme_pk: int) -> None:
    if not name or name in {LOGO_DESTINATION, FAVICON_DESTINATION}:
        return
    if Theme.objects.exclude(pk=theme_pk).filter(Q(logo=name) | Q(favicon=name)).exists():
        return
    if default_storage.exists(name):
        default_storage.delete(name)
