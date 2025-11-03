from __future__ import annotations

from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.core.management import call_command
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from syshealth.middleware import AccessLogMiddleware
from syshealth.models import AccessEvent, AccessSettings


class AccessLogMiddlewareTests(TestCase):
    def setUp(self):
        AccessSettings.get_cached(force=True)
        AccessEvent.objects.all().delete()
        self.factory = RequestFactory()
        self.middleware = AccessLogMiddleware(lambda request: HttpResponse("ok"))
        self.user = get_user_model().objects.create_user(
            username="tester", email="tester@example.com", password="123456", is_staff=True
        )

    def test_logs_authenticated_request(self):
        request = self.factory.get("/admin/")
        request.user = self.user
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

        event = AccessEvent.objects.get()
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.ip_address, "127.0.0.1")
        self.assertTrue(event.is_admin)

    def test_respects_ignore_paths(self):
        settings = AccessSettings.get_cached(force=True)
        settings.ignore_paths = ["/admin/ignore/"]
        settings.save()

        request = self.factory.get("/admin/ignore/test")
        request.user = self.user
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        self.middleware(request)
        self.assertFalse(AccessEvent.objects.exists())

    def test_skips_anonymous_when_disabled(self):
        settings = AccessSettings.get_cached(force=True)
        settings.log_anonymous = False
        settings.save()

        request = self.factory.get("/site/")
        request.user = AnonymousUser()
        request.META["REMOTE_ADDR"] = "127.0.0.2"

        self.middleware(request)
        self.assertFalse(AccessEvent.objects.exists())


class AccessDashboardViewTests(TestCase):
    def setUp(self):
        AccessSettings.get_cached(force=True)
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="test-pass",
            is_staff=True,
        )
        dashboard_perm = Permission.objects.get(
            content_type__app_label="ops", codename="view_access_dashboard"
        )
        event_perm = Permission.objects.get(
            content_type__app_label="ops", codename="view_access_event"
        )
        self.user.user_permissions.add(dashboard_perm, event_perm)
        self.client.force_login(self.user)

    def test_dashboard_requires_permission(self):
        another = get_user_model().objects.create_user(
            username="nope", email="nope@example.com", password="pass", is_staff=True
        )
        self.client.logout()
        self.client.force_login(another)

        response = self.client.get(reverse("admin:ops_access_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_renders_table(self):
        now = timezone.localtime()
        AccessEvent.objects.create(
            user=self.user,
            ip_address="127.0.0.1",
            path="/admin/",
            referrer="",
            user_agent="",
            is_admin=True,
            created_date=now.date(),
            created_time=now.time().replace(microsecond=0),
        )

        response = self.client.get(reverse("admin:ops_access_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monitoramento de acessos")
        self.assertIn("events_payload", response.context)
        payload = response.context["events_payload"]
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["source"], "Admin")

    def test_dashboard_json_endpoint(self):
        now = timezone.localtime()
        AccessEvent.objects.create(
            user=None,
            ip_address="10.0.0.1",
            path="/home/",
            referrer="",
            user_agent="",
            is_admin=False,
            created_date=now.date(),
            created_time=now.time().replace(microsecond=0),
        )

        response = self.client.get(reverse("admin:ops_access_dashboard_data"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("online", data)
        self.assertGreaterEqual(data["access_count"], 1)
        self.assertEqual(len(data["events"]), 1)
        self.assertEqual(data["events"][0]["source"], "Site")


class AccessEventPruneCommandTests(TestCase):
    def setUp(self):
        AccessSettings.get_cached(force=True)
        self.user = get_user_model().objects.create_user(
            username="archiver",
            email="archiver@example.com",
            password="test123",
            is_staff=True,
        )

    def test_prune_old_events(self):
        today = timezone.localdate()
        old_date = today - timedelta(days=120)
        AccessEvent.objects.bulk_create(
            [
                AccessEvent(
                    user=None,
                    ip_address="10.0.0.2",
                    path="/old/",
                    referrer="",
                    user_agent="",
                    is_admin=False,
                    created_date=old_date,
                    created_time=None,
                ),
                AccessEvent(
                    user=self.user,
                    ip_address="10.0.0.3",
                    path="/keep/",
                    referrer="",
                    user_agent="",
                    is_admin=True,
                    created_date=today,
                    created_time=timezone.localtime().time().replace(microsecond=0),
                ),
            ]
        )

        out = StringIO()
        call_command("ops_prune_access_events", stdout=out)
        output = out.getvalue()
        self.assertIn("Removidos", output)
        self.assertEqual(AccessEvent.objects.filter(path="/old/").count(), 0)
        self.assertEqual(AccessEvent.objects.filter(path="/keep/").count(), 1)

    def test_prune_dry_run(self):
        today = timezone.localdate()
        old_date = today - timedelta(days=91)
        AccessEvent.objects.create(
            user=None,
            ip_address="10.0.0.4",
            path="/maybe/",
            referrer="",
            user_agent="",
            is_admin=False,
            created_date=old_date,
            created_time=None,
        )

        out = StringIO()
        call_command("ops_prune_access_events", "--dry-run", stdout=out)
        output = out.getvalue()
        self.assertIn("Dry-run", output)
        self.assertEqual(AccessEvent.objects.filter(path="/maybe/").count(), 1)
