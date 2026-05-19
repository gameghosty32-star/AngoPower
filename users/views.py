import random
import string

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from .forms import CustomUserCreationForm
from customers.models import Customer


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            meter = f"MTR-{user.username}-{''.join(random.choices(string.digits, k=6))}"
            Customer.objects.create(
                user=user,
                meter_number=meter,
                customer_type='prepaid',
            )
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('customers:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
