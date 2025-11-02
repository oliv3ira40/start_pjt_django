from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemHealthPanel(models.Model):
    def __str__(self) -> str:
        return "Painel de saúde do servidor"

    class Meta:
        verbose_name = "Saúde do servidor"
        verbose_name_plural = "Saúde do servidor"


class SystemHealthConfig(models.Model):
    warn_cpu_load_per_core = models.FloatField(
        default=0.7,
        verbose_name="Alerta de carga por núcleo",
        help_text="Limite de atenção para carga média por núcleo (load1 / núcleos).",
    )
    crit_cpu_load_per_core = models.FloatField(
        default=1.0,
        verbose_name="Crítico de carga por núcleo",
        help_text="Limite crítico para carga média por núcleo (load1 / núcleos).",
    )
    warn_mem_used_pct = models.PositiveIntegerField(
        default=80,
        verbose_name="Alerta de uso de memória (%)",
        help_text="Limite de atenção para percentual de memória utilizada.",
    )
    crit_mem_used_pct = models.PositiveIntegerField(
        default=90,
        verbose_name="Crítico de uso de memória (%)",
        help_text="Limite crítico para percentual de memória utilizada.",
    )
    warn_disk_used_pct = models.PositiveIntegerField(
        default=80,
        verbose_name="Alerta de uso de disco (%)",
        help_text="Limite de atenção para percentual de disco utilizado.",
    )
    crit_disk_used_pct = models.PositiveIntegerField(
        default=90,
        verbose_name="Crítico de uso de disco (%)",
        help_text="Limite crítico para percentual de disco utilizado.",
    )
    cache_seconds = models.PositiveIntegerField(
        default=15,
        verbose_name="Tempo de cache (segundos)",
        help_text="Tempo de vida do cache das métricas antes de nova coleta.",
    )

    class Meta:
        verbose_name = "Configuração de saúde do servidor"
        verbose_name_plural = "Configurações de saúde do servidor"

    def __str__(self) -> str:
        return "Configuração de saúde do servidor"
