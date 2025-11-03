from __future__ import annotations

import logging
import random
from typing import Optional

from django.db import DatabaseError, IntegrityError
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from .models import AccessEvent, AccessSettings

logger = logging.getLogger(__name__)


class AccessLogMiddleware:
    """Registra eventos de acesso com o menor impacto possível."""

    def __init__(self, get_response):
        self.get_response = get_response
        self._error_count = 0
        self._admin_prefix: Optional[str] = None

    def __call__(self, request):
        response = self.get_response(request)
        self._log_request_safe(request)
        return response

    def _log_request_safe(self, request) -> None:
        try:
            self._log_request(request)
        except Exception:  # pragma: no cover - proteção extra
            self._error_count += 1
            if self._error_count <= 3:
                logger.exception("Falha ao registrar evento de acesso")

    def _log_request(self, request) -> None:
        settings = AccessSettings.get_cached()
        method = getattr(request, "method", "GET")
        if not settings.should_log_method(method):
            return

        path = getattr(request, "path", "") or ""
        if not path:
            return

        if settings.should_ignore_path(path):
            return

        user_agent = request.META.get("HTTP_USER_AGENT", "")[:256]
        if settings.should_ignore_user_agent(user_agent):
            return

        user = getattr(request, "user", None)
        user_instance = user if getattr(user, "is_authenticated", False) else None

        if user_instance is None and not settings.log_anonymous:
            return

        ip_address = self._get_ip(request)
        if user_instance is None and not ip_address:
            return

        sampling_ratio = max(settings.sampling_ratio or 1, 1)
        if sampling_ratio > 1 and random.randint(1, sampling_ratio) != 1:
            return

        is_admin = self._is_admin_request(request)
        now = timezone.localtime()
        created_time = now.time().replace(microsecond=0)

        event = AccessEvent(
            user=user_instance,
            ip_address=(ip_address or "")[:45],
            path=path[:512],
            referrer=request.META.get("HTTP_REFERER", "")[:512],
            user_agent=user_agent,
            is_admin=is_admin,
            created_date=now.date(),
            created_time=created_time,
        )

        try:
            event.save(force_insert=True)
        except (DatabaseError, IntegrityError):
            self._error_count += 1
            if self._error_count <= 3:
                logger.exception("Erro ao salvar evento de acesso")

    def _get_ip(self, request) -> str:
        header = request.META.get("HTTP_X_FORWARDED_FOR")
        if header:
            ip = header.split(",")[0].strip()
            if ip:
                return ip
        return request.META.get("REMOTE_ADDR", "")

    def _is_admin_request(self, request) -> bool:
        match = getattr(request, "resolver_match", None)
        if match and match.namespace and match.namespace.startswith("admin"):
            return True

        prefix = self._get_admin_prefix()
        if prefix and getattr(request, "path", "").startswith(prefix):
            return True
        return False

    def _get_admin_prefix(self) -> Optional[str]:
        if self._admin_prefix is not None:
            return self._admin_prefix

        try:
            url = reverse("admin:index")
        except NoReverseMatch:
            url = "/admin/"
        self._admin_prefix = url
        return url
