"""Template context for the configured administrative navigation."""

from django.contrib import admin


def configured_menu(request):
    """Expose the actual MenuConfig output to every Admin template.

    The standard Admin app list remains only the existing safe fallback when no
    active custom configuration can be built for the current request.
    """
    site = admin.site
    configured = None
    get_configured_menu = getattr(site, "get_configured_menu", None)
    if callable(get_configured_menu):
        configured = get_configured_menu(request)

    if configured is not None:
        return {
            "configured_admin_menu": configured,
            "configured_admin_menu_is_fallback": False,
        }

    get_app_list = getattr(site, "get_app_list", None)
    fallback = get_app_list(request) if callable(get_app_list) else []
    return {
        "configured_admin_menu": fallback,
        "configured_admin_menu_is_fallback": True,
    }
