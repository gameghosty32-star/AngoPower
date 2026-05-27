import random
import uuid

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError

from .models import Customer
from payments.models import Transaction
from payments.services import recharge_balance


def _generate_unique_meter_number(username):
    for _ in range(20):
        meter_number = f"MTR-{username}-{''.join(random.choices('0123456789', k=6))}"
        if not Customer.objects.filter(meter_number=meter_number).exists():
            return meter_number
    return f"MTR-{username}-{uuid.uuid4().hex[:8]}"


def _create_customer_for_user(user):
    meter_number = _generate_unique_meter_number(user.username)
    try:
        customer, _ = Customer.objects.get_or_create(
            user=user,
            defaults={
                'meter_number': meter_number,
                'customer_type': 'prepaid',
            }
        )
    except IntegrityError:
        fallback_meter = f"MTR-{user.username}-{uuid.uuid4().hex[:8]}"
        customer, _ = Customer.objects.get_or_create(
            user=user,
            defaults={
                'meter_number': fallback_meter,
                'customer_type': 'prepaid',
            }
        )
    return customer


def _get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        if getattr(user, 'user_type', None) == 'client':
            return _create_customer_for_user(user)
        raise


@login_required
def dashboard(request):
    try:
        customer = _get_customer(request.user)
    except Customer.DoesNotExist:
        return render(request, 'customers/no_profile.html')

    if customer.customer_type == 'prepaid':
        return redirect('prepaid:dashboard')
    return redirect('postpaid:dashboard')


@login_required
def check_balance(request):
    return redirect('prepaid:balance')


@login_required
def request_recharge(request):
    return redirect('prepaid:recharge')


@login_required
def transaction_history(request):
    return redirect('prepaid:transactions')
