from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ...models import AccessEvent, AccessSettings


class Command(BaseCommand):
    help = "Remove eventos de acesso antigos conforme a retenção configurada."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Somente calcula quantos registros seriam removidos.",
        )

    def handle(self, *args, **options):
        settings = AccessSettings.get_cached(force=True)
        retention_days = max(settings.retention_days, 1)
        cutoff_date = timezone.localdate() - timedelta(days=retention_days)

        queryset = AccessEvent.objects.filter(created_date__lt=cutoff_date)
        count = queryset.count()

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry-run: {count} eventos anteriores a {cutoff_date} seriam removidos."
                )
            )
            return

        with transaction.atomic():
            deleted, _ = queryset.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Removidos {deleted} eventos anteriores a {cutoff_date} (retenção {retention_days} dias)."
            )
        )
