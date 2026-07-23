from __future__ import annotations

import json
from pathlib import Path

from admin_interface.models import Theme
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

SEED_NAME = "theme_identity"
SEED_FILE_PATH = Path(__file__).resolve().parents[3] / "docs" / "seeds" / f"{SEED_NAME}.json"


def load_seed_theme_color_map() -> dict:
    if not SEED_FILE_PATH.exists():
        raise CommandError(f"Arquivo da seed nao encontrado: {SEED_FILE_PATH}")

    try:
        seed_payload = json.loads(SEED_FILE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CommandError(f"Arquivo da seed invalido ({SEED_FILE_PATH}): {exc}") from exc

    if not isinstance(seed_payload, dict):
        raise CommandError(f"Estrutura invalida em {SEED_FILE_PATH}: objeto raiz deve ser JSON object.")

    color_map = seed_payload.get("theme_color_map")
    if not isinstance(color_map, dict):
        raise CommandError(
            f"Seed '{SEED_NAME}' invalida em {SEED_FILE_PATH}: chave 'theme_color_map' obrigatoria."
        )
    if not color_map:
        raise CommandError(
            f"Seed '{SEED_NAME}' invalida em {SEED_FILE_PATH}: 'theme_color_map' nao pode ser vazio."
        )

    normalized_color_map = {}
    theme_field_names = {field.name for field in Theme._meta.get_fields() if hasattr(field, "attname")}
    for field_name, color_value in color_map.items():
        if field_name not in theme_field_names:
            raise CommandError(
                f"Campo '{field_name}' nao existe em admin_interface.Theme para seed '{SEED_NAME}'."
            )
        if not isinstance(color_value, str) or len(color_value) != 7 or not color_value.startswith("#"):
            raise CommandError(
                f"Valor invalido para '{field_name}' na seed '{SEED_NAME}': esperado hexadecimal no formato #RRGGBB."
            )
        try:
            int(color_value[1:], 16)
        except ValueError as exc:
            raise CommandError(
                f"Valor invalido para '{field_name}' na seed '{SEED_NAME}': esperado hexadecimal no formato #RRGGBB."
            ) from exc
        normalized_color_map[field_name] = color_value.upper()

    return normalized_color_map


class Command(BaseCommand):
    help = "Executa a seed de identidade visual do Finances Hub no tema ativo do admin_interface."

    def handle(self, *args, **options):
        theme_color_map = load_seed_theme_color_map()

        active_themes = Theme.objects.filter(active=True).order_by("pk")
        active_count = active_themes.count()

        if active_count == 0:
            raise CommandError("Nenhum tema ativo encontrado em admin_interface.Theme (active=True).")

        if active_count > 1:
            raise CommandError(
                f"Inconsistencia: foram encontrados {active_count} temas ativos em admin_interface.Theme (active=True)."
            )

        theme = active_themes.first()
        self.stdout.write(f"Tema ativo encontrado: id={theme.pk}, name='{theme.name}'")
        self.stdout.write(f"Seed executada: {SEED_NAME}")

        changed_fields = []
        for field_name, color_value in theme_color_map.items():
            if getattr(theme, field_name) != color_value:
                setattr(theme, field_name, color_value)
                changed_fields.append(field_name)

        with transaction.atomic():
            if changed_fields:
                theme.save(update_fields=changed_fields)

        applied_fields = list(theme_color_map.keys())
        self.stdout.write(f"Quantidade de campos mapeados aplicados: {len(applied_fields)}")
        self.stdout.write("Campos aplicados: " + ", ".join(applied_fields))
        self.stdout.write(f"Quantidade de campos atualizados: {len(changed_fields)}")

        if changed_fields:
            self.stdout.write("Campos efetivamente alterados: " + ", ".join(changed_fields))
        else:
            self.stdout.write("Campos efetivamente alterados: nenhum (tema ja estava atualizado)")

        self.stdout.write(self.style.SUCCESS("Seed de identidade visual aplicada com sucesso."))
