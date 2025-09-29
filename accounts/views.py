from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import SubscriptionUserCreationForm


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = SubscriptionUserCreationForm
    success_url = reverse_lazy("admin:login")

    def form_valid(self, form: UserCreationForm):
        user = form.save()
        group = Group.objects.filter(pk=1, name="assinante").first()
        if not group:
            group, _ = Group.objects.get_or_create(name="assinante")
        user.groups.add(group)
        messages.success(
            self.request,
            "Cadastro realizado com sucesso! Você já pode acessar com suas credenciais.",
        )
        return super().form_valid(form)
