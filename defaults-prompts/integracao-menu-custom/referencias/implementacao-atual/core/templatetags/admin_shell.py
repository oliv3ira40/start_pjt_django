"""Template helpers for the visual administrative shell."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_MODEL_ADMIN_VIEW_SUFFIXES = frozenset(
    {"add", "change", "changelist", "delete", "history"}
)


def _is_active(model, request):
    if not model or not request:
        return False
    view_name = getattr(getattr(request, "resolver_match", None), "view_name", "")
    if view_name and view_name == model.get("active_view_name"):
        return True
    active_view_prefix = model.get("active_view_prefix")
    view_suffix = view_name.removeprefix(active_view_prefix) if active_view_prefix else ""
    if view_suffix in _MODEL_ADMIN_VIEW_SUFFIXES:
        return True
    return model.get("admin_url") == request.path


@register.filter
def admin_menu_item_active(model, request):
    return _is_active(model, request)


@register.filter
def admin_menu_group_active(models, request):
    return any(_is_active(model, request) for model in models)


_MENU_ICON_PATHS = {
    "apiary": '<path d="M5 8.5 12 4l7 4.5v8L12 21l-7-4.5v-8Z"/><path d="M8 10h8M8 14h8M12 4v17" stroke-width="1.5" opacity=".7"/>',
    "chevron": '<path d="m7 9.5 5 5 5-5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "chart": '<path d="M6 19V9M12 19V5M18 19v-7" stroke-width="2" stroke-linecap="round"/><path d="M4 19h16" stroke-width="1.8" stroke-linecap="round"/>',
    "collapse": '<path d="m14 6-6 6 6 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "clipboard": '<rect x="5" y="5" width="14" height="15" rx="2"/><path d="M9 5V3h6v2M8.5 10h7M8.5 14h7" stroke-linecap="round"/>',
    "close": '<path d="m6 6 12 12M18 6 6 18" stroke-width="2" stroke-linecap="round"/>',
    "folder": '<path d="M4 7.5h6l1.8 2H20v8.8A1.7 1.7 0 0 1 18.3 20H5.7A1.7 1.7 0 0 1 4 18.3V7.5Z"/>',
    "logout": '<path d="M10 5H6a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h4M14 8l4 4-4 4M18 12H9" stroke-linecap="round" stroke-linejoin="round"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16" stroke-width="2" stroke-linecap="round"/>',
    "history": '<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3L4.5 9" stroke-linecap="round" stroke-linejoin="round"/><path d="M4.5 5.5V9h3.5M12 8v4l2.8 1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    "hive": '<path d="M7 5h10l2 4v10H5V9l2-4Z"/><path d="M5 9h14M9 13h6M9 16h6" stroke-linecap="round"/>',
    "image": '<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="m6.5 17 4-4 2.5 2 2-2 2.5 4" stroke-linecap="round" stroke-linejoin="round"/>',
    "link": '<path d="M10 13.8a4 4 0 0 0 5.7.1l2-2a4 4 0 0 0-5.7-5.7l-1.1 1.1M14 10.2a4 4 0 0 0-5.7-.1l-2 2a4 4 0 0 0 5.7 5.7l1.1-1.1" stroke-linecap="round"/>',
    "map-pin": '<path d="M12 21s6-5.2 6-11a6 6 0 1 0-12 0c0 5.8 6 11 6 11Z"/><circle cx="12" cy="10" r="2.2"/>',
    "privacy": '<path d="M12 3 19 6v5c0 4.7-2.4 7.8-7 10-4.6-2.2-7-5.3-7-10V6l7-3Z"/><path d="M9.5 12 11 13.5l3.5-4" stroke-linecap="round" stroke-linejoin="round"/>',
    "search": '<circle cx="10.7" cy="10.7" r="6.2"/><path d="m15.4 15.4 4.1 4.1" stroke-linecap="round"/>',
    "site": '<path d="M14 5h5v5M19 5l-8 8M19 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5" stroke-linecap="round" stroke-linejoin="round"/>',
    "subscriptions": '<rect x="4" y="6" width="16" height="12" rx="2"/><path d="M4 10h16M8 14h4" stroke-linecap="round"/>',
    "tools": '<path d="M14.7 6.2a4.1 4.1 0 0 0-5.2 5.2L4.3 16.6a1.8 1.8 0 1 0 2.5 2.5l5.2-5.2a4.1 4.1 0 0 0 5.2-5.2l-2.5 2.5-2.4-2.4 2.4-2.6Z" stroke-linejoin="round"/>',
    "user": '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 19c.8-3.6 3-5.4 6.5-5.4s5.7 1.8 6.5 5.4" stroke-linecap="round"/>',
}


@register.simple_tag
def admin_shell_icon(name):
    """Render the approved line icon for a menu semantic identifier."""

    paths = _MENU_ICON_PATHS.get(name, _MENU_ICON_PATHS["folder"])
    return mark_safe(
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" '
        'fill="none" stroke="currentColor" stroke-width="1.8">'
        f"{paths}</svg>"
    )
