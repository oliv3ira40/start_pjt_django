from __future__ import annotations

import time
from datetime import datetime
from typing import Iterable, List

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AccessEventQuerySet(models.QuerySet):
    def since(self, moment: datetime) -> "AccessEventQuerySet":
        if moment is None:
            return self

        local_moment = timezone.localtime(moment)
        moment_date = local_moment.date()
        moment_time = local_moment.time()

        return self.filter(
            models.Q(created_date__gt=moment_date)
            | (
                models.Q(created_date=moment_date)
                & (
                    models.Q(created_time__gte=moment_time)
                    | models.Q(created_time__isnull=True)
                )
            )
        )


class AccessDashboard(models.Model):
    class Meta:
        verbose_name = "Monitoramento de acessos"
        verbose_name_plural = "Monitoramento de acessos"
        default_permissions = ()
        permissions = (
            ("view_access_dashboard", "Pode visualizar o dashboard de acessos"),
        )

    def __str__(self) -> str:
        return "Dashboard de acessos"


class AccessEvent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="access_events",
        verbose_name="Usuário",
    )
    ip_address = models.CharField("Endereço IP", max_length=45, blank=True)
    path = models.CharField("Caminho", max_length=512)
    referrer = models.CharField("Origem (referer)", max_length=512, blank=True)
    user_agent = models.CharField("User agent", max_length=256, blank=True)
    is_admin = models.BooleanField("Origem: admin?", default=False)
    created_date = models.DateField("Data do acesso")
    created_time = models.TimeField("Hora do acesso", null=True, blank=True)

    objects = AccessEventQuerySet.as_manager()

    class Meta:
        verbose_name = "Evento de acesso"
        verbose_name_plural = "Eventos de acesso"
        default_permissions = ()
        indexes = [
            models.Index(fields=["created_date"], name="ops_access_date_idx"),
            models.Index(
                fields=["created_date", "created_time"],
                name="ops_access_datetime_idx",
            ),
            models.Index(fields=["user"], name="ops_access_user_idx"),
            models.Index(fields=["ip_address"], name="ops_access_ip_idx"),
            models.Index(fields=["is_admin"], name="ops_access_admin_idx"),
        ]
        ordering = ("-created_date", "-created_time", "-pk")
        permissions = (("view_access_event", "Pode visualizar eventos de acesso"),)

    def __str__(self) -> str:
        target = self.user.get_username() if self.user_id else self.ip_address
        return f"Acesso {target or 'desconhecido'} em {self.path}"


class AccessSettings(models.Model):
    online_window_minutes = models.PositiveIntegerField(
        default=5,
        verbose_name="Janela de usuários online (min)",
        help_text="Intervalo considerado para usuários online e métricas em minutos.",
    )
    auto_refresh_seconds = models.PositiveIntegerField(
        default=10,
        verbose_name="Intervalo de auto atualização (s)",
        help_text="Tempo entre atualizações automáticas do dashboard em segundos.",
    )
    log_anonymous = models.BooleanField(
        default=True,
        verbose_name="Registrar visitantes anônimos",
        help_text="Desative para registrar apenas usuários autenticados.",
    )
    log_non_get_requests = models.BooleanField(
        default=False,
        verbose_name="Registrar métodos não-GET",
        help_text="Habilite para registrar requisições que não sejam GET.",
    )
    ignore_paths = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Caminhos ignorados",
        help_text="Lista de prefixes de caminhos a ignorar (ex.: /static/).",
    )
    sampling_ratio = models.PositiveIntegerField(
        default=1,
        verbose_name="Amostragem",
        help_text="1 registra todos os acessos; valores maiores registram 1 a cada N acessos.",
    )
    retention_days = models.PositiveIntegerField(
        default=90,
        verbose_name="Retenção (dias)",
        help_text="Eventos com idade superior serão removidos pela limpeza agendada.",
    )
    ignored_user_agents = models.JSONField(
        default=list,
        blank=True,
        verbose_name="User agents ignorados",
        help_text="Substrings simples para identificar crawlers a ignorar.",
    )

    class Meta:
        verbose_name = "Configuração de monitoramento de acesso"
        verbose_name_plural = "Configurações de monitoramento de acesso"

    _CACHE_SECONDS = 60
    _cached_instance: "AccessSettings | None" = None
    _cached_at: float | None = None

    def __str__(self) -> str:
        return "Configuração de monitoramento de acessos"

    @classmethod
    def get_cached(cls, force: bool = False) -> "AccessSettings":
        now = time.monotonic()
        if (
            not force
            and cls._cached_instance is not None
            and cls._cached_at is not None
            and now - cls._cached_at < cls._CACHE_SECONDS
        ):
            return cls._cached_instance

        instance = cls.objects.first()
        if instance is None:
            instance = cls.objects.create(
                ignore_paths=["/static/", "/media/", "/health/"],
            )

        cls._cached_instance = instance
        cls._cached_at = now
        return instance

    @property
    def normalized_ignore_paths(self) -> List[str]:
        values: Iterable[str]
        raw = self.ignore_paths or []
        if isinstance(raw, str):
            values = [value.strip() for value in raw.split(",") if value.strip()]
        else:
            values = [str(value).strip() for value in raw if str(value).strip()]
        return [value.rstrip("*") for value in values]

    @property
    def normalized_user_agents(self) -> List[str]:
        raw = self.ignored_user_agents or []
        if isinstance(raw, str):
            return [value.strip().lower() for value in raw.split(",") if value.strip()]
        return [str(value).strip().lower() for value in raw if str(value).strip()]

    def should_log_method(self, method: str) -> bool:
        if self.log_non_get_requests:
            return True
        return method.upper() == "GET"

    def should_ignore_path(self, path: str) -> bool:
        for prefix in self.normalized_ignore_paths:
            if path.startswith(prefix):
                return True
        return False

    def should_ignore_user_agent(self, user_agent: str) -> bool:
        if not user_agent:
            return False
        user_agent_lower = user_agent.lower()
        for entry in self.normalized_user_agents:
            if entry and entry in user_agent_lower:
                return True
        return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.__class__._cached_instance = self
        self.__class__._cached_at = time.monotonic()


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
