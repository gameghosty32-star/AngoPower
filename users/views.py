import random
import string
import uuid

from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from .forms import CustomUserCreationForm
from customers.models import Customer


def _generate_unique_meter_number(username):
    for _ in range(20):
        meter_number = f"MTR-{username}-{''.join(random.choices(string.digits, k=6))}"
        if not Customer.objects.filter(meter_number=meter_number).exists():
            return meter_number
    return f"MTR-{username}-{uuid.uuid4().hex[:8]}"


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            meter_number = _generate_unique_meter_number(user.username)
            try:
                Customer.objects.get_or_create(
                    user=user,
                    defaults={
                        'meter_number': meter_number,
                        'customer_type': 'prepaid',
                    }
                )
            except IntegrityError:
                fallback_meter = f"MTR-{user.username}-{uuid.uuid4().hex[:8]}"
                Customer.objects.get_or_create(
                    user=user,
                    defaults={
                        'meter_number': fallback_meter,
                        'customer_type': 'prepaid',
                    }
                )
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('customers:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
