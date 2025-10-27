from __future__ import annotations

from django.contrib import admin

from .models import MenuConfig, MenuItem


class MenuItemInline(admin.TabularInline):
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
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(MenuConfig)
class MenuConfigAdmin(admin.ModelAdmin):
    list_display = ("scope", "active", "updated_at")
    list_filter = ("scope", "active")
    search_fields = ("scope",)
    ordering = ("scope", "-updated_at")
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


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "config",
        "order",
        "item_type",
        "label",
        "app_label",
        "model_name",
        "url_name",
    )
    list_filter = ("item_type", "config__scope")
    search_fields = ("label", "app_label", "model_name", "url_name")
    ordering = ("config", "order", "pk")

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
