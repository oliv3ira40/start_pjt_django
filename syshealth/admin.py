from __future__ import annotations

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import SystemHealthConfig, SystemHealthPanel


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
