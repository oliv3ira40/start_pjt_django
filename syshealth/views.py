from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse

from .metrics import get_system_health_snapshot
from .models import SystemHealthConfig


def _admin_namespace(request) -> str:
    match = getattr(request, "resolver_match", None)
    if match and match.namespace:
        return match.namespace
    return "admin"


@staff_member_required
def dashboard(request):
    if not request.user.has_perm("syshealth.view_systemhealthpanel"):
        raise PermissionDenied

    force_refresh = request.GET.get("refresh") == "1"
    snapshot = get_system_health_snapshot(force_refresh=force_refresh)
    config = SystemHealthConfig.objects.first()

    admin_namespace = _admin_namespace(request)
    refresh_url = f"{reverse(f'{admin_namespace}:syshealth_dashboard')}?refresh=1"
    config_url = None
    if config and request.user.is_superuser:
        config_url = reverse(
            f"{admin_namespace}:syshealth_systemhealthconfig_change", args=[config.pk]
        )

    context = {
        "title": "Saúde do servidor",
        "refresh_url": refresh_url,
        "config_url": config_url,
        "config": config,
        **snapshot,
    }
    return render(request, "admin/syshealth/dashboard.html", context)
