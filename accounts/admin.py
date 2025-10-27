from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Person

User = get_user_model()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "first_name", "last_name")
    search_fields = ("user__username", "first_name", "last_name", "email")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user")
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_view_permission(request, obj)
        if obj is None:
            return True
        return obj.user == request.user

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return super().has_add_permission(request)
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_delete_permission(request, obj)
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_change_permission(request, obj)
        if obj is None:
            return True
        return obj.user == request.user

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ("user", "email", "first_name", "last_name", "created_at", "updated_at")
        return ("email", "first_name", "last_name")

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ("created_at", "updated_at")
        return ()

    def message_user(self, request, message, level=messages.INFO, extra_tags="", fail_silently=False):
        if (
            level == messages.SUCCESS
            and request.method == "POST"
            and getattr(request, "resolver_match", None)
            and "object_id" in request.resolver_match.kwargs
        ):
            message = _("Dados do perfil atualizados.")
        super().message_user(request, message, level=level, extra_tags=extra_tags, fail_silently=fail_silently)


class RestrictedUserAdmin(DjangoUserAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class RestrictedGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


for model, admin_class in (
    (User, RestrictedUserAdmin),
    (Group, RestrictedGroupAdmin),
):
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
    admin.site.register(model, admin_class)
