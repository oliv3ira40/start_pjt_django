from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import render, redirect



def register(request):
    """
    Display and process the user registration form.

    When the form is submitted and valid, a new user is created and added
    to the 'assinante' group (creating the group if needed). After successful
    registration the user is redirected to the admin login page.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()

            # Ensure the group exists. If it doesn't exist, create it.
            group, _ = Group.objects.get_or_create(name='assinante')
            # Add the new user to the group
            user.groups.add(group)

            # Provide feedback to the user
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')

            # Redirect to the admin login page
            return redirect('admin:login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
