from __future__ import annotations

import csv
from datetime import datetime, time as time_cls, timedelta
from io import StringIO
from typing import Dict, Iterable, Tuple

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, Paginator
from django.db.models import QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.timesince import timesince

from .metrics import get_system_health_snapshot
from .models import AccessEvent, AccessSettings, SystemHealthConfig
from .forms import AccessEventFilterForm


def _admin_namespace(request) -> str:
    match = getattr(request, "resolver_match", None)
    if match and match.namespace:
        return match.namespace
    return "admin"


def _user_can_view_dashboard(user) -> bool:
    return bool(user and (user.is_superuser or user.has_perm("ops.view_access_dashboard")))


def _user_can_view_events(user) -> bool:
    return bool(user and (user.is_superuser or user.has_perm("ops.view_access_event")))


def _combine_event_datetime(event) -> datetime:
    event_time = event.created_time or time_cls(0, 0, 0)
    naive = datetime.combine(event.created_date, event_time)
    if timezone.is_naive(naive):
        return timezone.make_aware(naive, timezone.get_current_timezone())
    return naive


def _relative_time_display(moment: datetime, now: datetime) -> str:
    delta = now - moment
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    if total_seconds < 60:
        return f"há {total_seconds}s"
    if total_seconds < 3600:
        minutes = total_seconds // 60
        return f"há {minutes}min"
    if total_seconds < 86400:
        hours = total_seconds // 3600
        return f"há {hours}h"
    return f"há {timesince(moment, now=now)}"


def _window_start(now: datetime, minutes: int) -> datetime:
    return now - timedelta(minutes=minutes)


def _build_base_queryset(start: datetime) -> QuerySet:
    return AccessEvent.objects.select_related("user").since(start)


def _apply_filters(qs, filters: Dict[str, object]):
    if not filters:
        return qs
    return qs.filter(**filters)


def _compute_online_counts(qs: QuerySet) -> Tuple[int, int]:
    authenticated = (
        qs.exclude(user_id__isnull=True)
        .values_list("user_id", flat=True)
        .distinct()
        .count()
    )
    anonymous = (
        qs.filter(user_id__isnull=True)
        .exclude(ip_address="")
        .values_list("ip_address", flat=True)
        .distinct()
        .count()
    )
    return authenticated, anonymous


def _serialize_event(event, admin_namespace: str) -> Dict[str, object]:
    event_dt = _combine_event_datetime(event)
    now = timezone.localtime()
    user_display = "Visitante"
    user_url = None
    if event.user:
        user_display = event.user.get_username()
        try:
            user_url = reverse(f"{admin_namespace}:auth_user_change", args=[event.user.pk])
        except Exception:  # pragma: no cover - fallback se admin não tiver rota
            user_url = None

    return {
        "id": event.pk,
        "relative_time": _relative_time_display(event_dt, now),
        "timestamp": event_dt.isoformat(),
        "user": user_display,
        "user_url": user_url,
        "ip_address": event.ip_address,
        "path": event.path,
        "referrer": event.referrer,
        "source": "Admin" if event.is_admin else "Site",
    }


def _generate_csv_response(events: Iterable[AccessEvent], now: datetime) -> HttpResponse:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["timestamp", "usuario", "ip", "path", "origem", "referrer"])
    for event in events:
        dt = _combine_event_datetime(event)
        username = event.user.get_username() if event.user else "Visitante"
        writer.writerow(
            [
                dt.isoformat(),
                username,
                event.ip_address,
                event.path,
                "admin" if event.is_admin else "site",
                event.referrer,
            ]
        )

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename=access-events-{now:%Y%m%d%H%M%S}.csv"
    return response


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


@staff_member_required
def access_dashboard(request):
    if not _user_can_view_dashboard(request.user):
        raise PermissionDenied

    settings_obj = AccessSettings.get_cached()
    now = timezone.localtime()
    window_start = _window_start(now, settings_obj.online_window_minutes)

    base_qs = _build_base_queryset(window_start)
    online_authenticated, online_anonymous = _compute_online_counts(base_qs)
    online_total = online_authenticated + online_anonymous
    access_count = base_qs.count()

    user_ids = (
        AccessEvent.objects.exclude(user_id__isnull=True)
        .values_list("user_id", flat=True)
        .distinct()
    )
    user_queryset = get_user_model().objects.filter(id__in=user_ids)

    filter_form = AccessEventFilterForm(request.GET or None, user_queryset=user_queryset)
    filters = filter_form.cleaned_filters()
    filtered_qs = _apply_filters(base_qs, filters)

    paginator = Paginator(filtered_qs, 50)
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(1)

    admin_namespace = _admin_namespace(request)
    data_url = reverse(f"{admin_namespace}:ops_access_dashboard_data")

    health_snapshot = get_system_health_snapshot(force_refresh=False)

    if request.GET.get("export") == "csv":
        if not _user_can_view_events(request.user):
            raise PermissionDenied
        return _generate_csv_response(filtered_qs, now)

    query_params = request.GET.copy()
    full_query_string = query_params.urlencode()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    events_payload = [_serialize_event(event, admin_namespace) for event in page_obj.object_list]

    context = {
        "title": "Monitoramento de acessos",
        "online_count": online_total,
        "access_count": access_count,
        "online_authenticated": online_authenticated,
        "online_anonymous": online_anonymous,
        "online_window_minutes": settings_obj.online_window_minutes,
        "auto_refresh_seconds": settings_obj.auto_refresh_seconds,
        "page_obj": page_obj,
        "events": page_obj.object_list,
        "events_payload": events_payload,
        "filter_form": filter_form,
        "data_url": data_url,
        "health_snapshot": health_snapshot,
        "now": now,
        "settings": settings_obj,
        "query_string": query_string,
        "full_query_string": full_query_string,
    }
    return render(request, "admin/ops/access_dashboard.html", context)


@staff_member_required
def access_dashboard_data(request):
    if not _user_can_view_dashboard(request.user):
        raise PermissionDenied

    settings_obj = AccessSettings.get_cached()
    now = timezone.localtime()
    window_start = _window_start(now, settings_obj.online_window_minutes)
    base_qs = _build_base_queryset(window_start)

    user_ids = (
        AccessEvent.objects.exclude(user_id__isnull=True)
        .values_list("user_id", flat=True)
        .distinct()
    )
    user_queryset = get_user_model().objects.filter(id__in=user_ids)
    filter_form = AccessEventFilterForm(request.GET or None, user_queryset=user_queryset)
    filters = filter_form.cleaned_filters()
    filtered_qs = _apply_filters(base_qs, filters)

    paginator = Paginator(filtered_qs, 50)
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(1)

    admin_namespace = _admin_namespace(request)
    events_payload = [_serialize_event(event, admin_namespace) for event in page_obj.object_list]
    online_authenticated, online_anonymous = _compute_online_counts(base_qs)
    online_total = online_authenticated + online_anonymous
    access_count = base_qs.count()

    response_data = {
        "online": {
            "total": online_total,
            "authenticated": online_authenticated,
            "anonymous": online_anonymous,
            "window_minutes": settings_obj.online_window_minutes,
        },
        "access_count": access_count,
        "events": events_payload,
        "page": {
            "number": page_obj.number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        },
        "generated_at": now.isoformat(),
    }
    return JsonResponse(response_data)
