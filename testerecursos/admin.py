from django.contrib import admin

from .forms import ThreeResourcesForm
from .models import ThreeResources


@admin.register(ThreeResources)
class ThreeResourcesAdmin(admin.ModelAdmin):
    form = ThreeResourcesForm
    fields = ["photo", "yes_no", "description", "option"]
    list_display = ["id", "yes_no", "option"]
    list_filter = ["yes_no", "option"]

    class Media:
        js = ("admin/testerecursos/threeresources-rules.js",)
