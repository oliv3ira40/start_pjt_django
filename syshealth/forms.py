from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model


class AccessEventFilterForm(forms.Form):
    SOURCE_ALL = "all"
    SOURCE_ADMIN = "admin"
    SOURCE_SITE = "site"

    SOURCE_CHOICES = (
        (SOURCE_ALL, "Todos"),
        (SOURCE_ADMIN, "Admin"),
        (SOURCE_SITE, "Site público"),
    )

    source = forms.ChoiceField(
        label="Origem",
        required=False,
        choices=SOURCE_CHOICES,
        initial=SOURCE_ALL,
    )
    user = forms.ModelChoiceField(
        label="Usuário",
        required=False,
        queryset=get_user_model().objects.none(),
    )
    query = forms.CharField(
        label="Path contém",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "/minha/url"}),
    )

    def __init__(self, *args, **kwargs):
        user_queryset = kwargs.pop("user_queryset", None)
        super().__init__(*args, **kwargs)
        if user_queryset is None:
            user_queryset = get_user_model().objects.none()
        self.fields["user"].queryset = user_queryset.order_by("username")
        self.fields["user"].empty_label = "Todos"

    def cleaned_filters(self) -> dict:
        if not self.is_valid():
            return {}
        data = self.cleaned_data
        filters = {}
        source = data.get("source") or self.SOURCE_ALL
        if source == self.SOURCE_ADMIN:
            filters["is_admin"] = True
        elif source == self.SOURCE_SITE:
            filters["is_admin"] = False

        if data.get("user"):
            filters["user_id"] = data["user"].pk

        if data.get("query"):
            filters["path__icontains"] = data["query"]
        return filters
