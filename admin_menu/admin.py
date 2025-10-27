from __future__ import annotations

from django.contrib import admin

from core.admin import BaseAdmin, BaseInline

from .models import MenuConfig, MenuItem, MenuScope


class MenuItemInline(BaseInline):
    model = MenuItem
    extra = 0
    fields = (
        "order",
        "item_type",
        "section",
        "label",
        "app_label",
        "model_name",
        "url_name",
        "absolute_url",
        "permission_codename",
    )
    ordering = ("order", "pk")
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(MenuScope)
class MenuScopeAdmin(BaseAdmin):
    list_display = ("name", "group", "priority")
    list_filter = ("group",)
    search_fields = ("name", "group__name")
    ordering = ("-priority", "name")

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(MenuConfig)
class MenuConfigAdmin(BaseAdmin):
    list_display = ("scope", "is_active", "updated_at")
    list_filter = ("scope__name", "is_active")
    search_fields = ("scope__name",)
    ordering = ("scope__priority", "scope__name", "-updated_at")
    inlines = (MenuItemInline,)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
