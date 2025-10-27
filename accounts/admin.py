from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from core.admin import BaseAdmin, Select2AdminMixin

from .models import Person

User = get_user_model()


@admin.register(Person)
class PersonAdmin(BaseAdmin):
    list_display = ("user", "email", "first_name", "last_name")
    search_fields = ("user__username", "first_name", "last_name", "email")

    def changelist_view(self, request, extra_context=None):
        if request.user.is_superuser:
            return super().changelist_view(request, extra_context=extra_context)

        try:
            person, _ = Person.objects.get_or_create(
                user=request.user,
                defaults={
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "email": request.user.email,
                },
            )
        except Exception:  # pragma: no cover - defensive fallback
            return HttpResponseForbidden(_("Não foi possível localizar o seu perfil."))

        return redirect("admin:accounts_person_change", person.pk)

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

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ("created_at", "updated_at")
        return ("created_at", "updated_at")

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if request.user.is_superuser:
            return fields
        return [field for field in fields if field != "user"]


class RestrictedUserAdmin(Select2AdminMixin, DjangoUserAdmin):
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


class RestrictedGroupAdmin(Select2AdminMixin, GroupAdmin):
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
