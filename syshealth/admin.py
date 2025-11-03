from __future__ import annotations

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import Truncator

from .models import (
    AccessDashboard,
    AccessEvent,
    AccessSettings,
    SystemHealthConfig,
    SystemHealthPanel,
)


def _has_ops_permission(user, codename: str) -> bool:
    if not user:
        return False
    return bool(
        user.is_superuser
        or user.has_perm(f"ops.{codename}")
        or user.has_perm(f"syshealth.{codename}")
    )


@admin.register(AccessDashboard)
class AccessDashboardAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return _has_ops_permission(request.user, "view_access_dashboard")

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        url = reverse(f"{self.admin_site.name}:ops_access_dashboard")
        return HttpResponseRedirect(url)


@admin.register(AccessEvent)
class AccessEventAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "created_at_display",
        "user_display",
        "ip_address",
        "path_short",
        "origin_display",
    )
    list_filter = (
        "is_admin",
        "created_date",
        ("user", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("path", "referrer", "ip_address", "user__username", "user__email")
    readonly_fields = (
        "user",
        "ip_address",
        "path",
        "referrer",
        "user_agent",
        "is_admin",
        "created_date",
        "created_time",
    )
    list_per_page = 50
    date_hierarchy = "created_date"

    def has_module_permission(self, request):
        return self.has_view_permission(request)

    def has_view_permission(self, request, obj=None):
        return _has_ops_permission(request.user, "view_access_event")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    @admin.display(description="Data/Hora", ordering=("created_date", "created_time"))
    def created_at_display(self, obj):
        if obj.created_time:
            return f"{obj.created_date} {obj.created_time}"
        return str(obj.created_date)

    @admin.display(description="Usuário", ordering="user__username")
    def user_display(self, obj):
        if obj.user:
            return obj.user.get_username()
        return "Visitante"

    @admin.display(description="Origem")
    def origin_display(self, obj):
        return "Admin" if obj.is_admin else "Site"

    @admin.display(description="Path")
    def path_short(self, obj):
        if len(obj.path) <= 64:
            return obj.path
        truncated = Truncator(obj.path).chars(64)
        return format_html('<span title="{}">{}</span>', obj.path, truncated)


@admin.register(SystemHealthPanel)
class SystemHealthPanelAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        url = reverse(f"{self.admin_site.name}:syshealth_dashboard")
        return HttpResponseRedirect(url)


@admin.register(SystemHealthConfig)
class SystemHealthConfigAdmin(admin.ModelAdmin):
    list_display = (
        "warn_cpu_load_per_core",
        "crit_cpu_load_per_core",
        "warn_mem_used_pct",
        "crit_mem_used_pct",
        "warn_disk_used_pct",
        "crit_disk_used_pct",
        "cache_seconds",
    )

    def has_module_permission(self, request):
        return bool(request.user and request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def has_add_permission(self, request):
        return bool(request.user and request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)


@admin.register(AccessSettings)
class AccessSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "online_window_minutes",
        "auto_refresh_seconds",
        "sampling_ratio",
        "log_anonymous",
        "log_non_get_requests",
    )

    def has_module_permission(self, request):
        return bool(request.user and request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
