from __future__ import annotations

from django import forms

from .models import ThreeResources


class ThreeResourcesForm(forms.ModelForm):
    class Meta:
        model = ThreeResources
        fields = ["photo", "yes_no", "description", "option"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        photo_field = self.fields.get("photo")
        if photo_field is not None:
            photo_field.widget.attrs["data-admin-preview"] = "image"
        yes_no_field = self.fields.get("yes_no")
        if yes_no_field is not None:
            yes_no_field.widget = forms.RadioSelect(choices=yes_no_field.choices)
        option_field = self.fields.get("option")
        if option_field is not None:
            option_field.widget.attrs["data-select2"] = "1"

    def clean(self):
        cleaned_data = super().clean()
        yes_no = cleaned_data.get("yes_no")
        description = cleaned_data.get("description")
        if yes_no == ThreeResources.YesNoChoices.SIM and not description:
            self.add_error("description", "Este campo é obrigatório quando 'Sim ou não' está marcado como Sim.")
        return cleaned_data
