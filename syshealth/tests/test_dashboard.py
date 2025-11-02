from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from syshealth.models import SystemHealthPanel

User = get_user_model()


def build_snapshot() -> dict:
    return {
        "hostname": "host-test",
        "system_platform": "Linux-5.10",
        "kernel": "5.10.0",
        "python_version": "3.11.0",
        "local_time": datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
        "cpu": {
            "cores": 4,
            "cores_display": "4",
            "load": (0.1, 0.2, 0.3),
            "load_display": "0.10 / 0.20 / 0.30",
            "load_per_core": 0.025,
            "load_per_core_display": "0.03",
            "status": "ok",
            "status_label": "OK",
        },
        "memory": {
            "total": 1024,
            "used": 512,
            "percent": 50.0,
            "total_display": "1.00 KB",
            "used_display": "512 B",
            "percent_display": "50.0%",
            "status": "ok",
            "status_label": "OK",
        },
        "disk": {
            "total": 2048,
            "used": 1024,
            "free": 1024,
            "percent": 50.0,
            "total_display": "2.00 KB",
            "used_display": "1.00 KB",
            "free_display": "1.00 KB",
            "percent_display": "50.0%",
            "status": "ok",
            "status_label": "OK",
        },
        "uptime": {
            "seconds": 3600.0,
            "display": "1 hora",
        },
        "summary_text": "Resumo de teste",
        "cache_seconds": 15,
    }


class DashboardViewTests(TestCase):
    def setUp(self):
        self.permission = Permission.objects.get(codename="view_systemhealthpanel")
        # Garantir que o modelo âncora exista para registro de permissões em testes
        SystemHealthPanel.objects.create()

    def _create_user(self, has_permission: bool) -> User:
        user = User.objects.create_user(
            username=f"user_{'perm' if has_permission else 'noperm'}",
            password="pass1234",
            is_staff=True,
        )
        if has_permission:
            user.user_permissions.add(self.permission)
        return user

    def test_dashboard_requires_view_permission(self):
        user = self._create_user(has_permission=False)
        self.client.force_login(user)
        response = self.client.get(reverse("admin:syshealth_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_renders_for_authorized_user(self):
        user = self._create_user(has_permission=True)
        self.client.force_login(user)

        snapshot = build_snapshot()
        with patch("syshealth.views.get_system_health_snapshot", return_value=snapshot):
            response = self.client.get(reverse("admin:syshealth_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saúde do servidor")
        self.assertEqual(response.context["summary_text"], "Resumo de teste")
        self.assertContains(response, "Atualizar agora")

    def test_refresh_query_param_bypasses_cache(self):
        user = self._create_user(has_permission=True)
        self.client.force_login(user)

        snapshot = build_snapshot()
        with patch("syshealth.views.get_system_health_snapshot", return_value=snapshot) as mocked:
            response = self.client.get(reverse("admin:syshealth_dashboard"), {"refresh": "1"})

        self.assertEqual(response.status_code, 200)
        mocked.assert_called_once_with(force_refresh=True)

    def test_changelist_redirects_to_dashboard(self):
        user = self._create_user(has_permission=True)
        self.client.force_login(user)
        response = self.client.get(reverse("admin:syshealth_systemhealthpanel_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin:syshealth_dashboard"))
