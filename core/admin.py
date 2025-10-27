from django.contrib import admin


class Select2AdminMixin:
    """Mixin that wires the shared Select2 and helper assets into the admin."""

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
                "apiary/css/image-preview.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.full.min.js",
            "apiary/js/hive_species_filter.js",
            "apiary/js/conditional-fields.js",
            "apiary/js/image-preview.js",
        )


class BaseAdmin(Select2AdminMixin, admin.ModelAdmin):
    """Base admin that enables the reusable JS-only helpers."""


class BaseInline(Select2AdminMixin, admin.TabularInline):
    """Base inline with the same helper assets wired in."""
