from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from customers.models import Customer
from customers.views import _get_customer
from . import services


@login_required
def dashboard(request):
    customer = _get_customer(request.user)
    recent_transactions = services.get_transaction_history(customer.pk, limit=5)
    return render(request, 'prepaid/dashboard.html', {
        'customer': customer,
        'recent_transactions': recent_transactions,
    })


@login_required
def check_balance(request):
    customer = _get_customer(request.user)
    return render(request, 'prepaid/balance.html', {
        'customer': customer,
    })


@login_required
def request_recharge(request):
    customer = _get_customer(request.user)
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount <= 0:
                raise ValueError('Amount must be positive')
            return redirect(f"{reverse('payment_gateways:select', kwargs={'context_key': 'recharge', 'context_value': '0'})}?amount={amount}")
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
    return render(request, 'prepaid/recharge.html', {
        'customer': customer,
    })


@login_required
def transaction_history(request):
    customer = _get_customer(request.user)
    transactions = services.get_transaction_history(customer.pk)
    return render(request, 'prepaid/transaction_history.html', {
        'customer': customer,
        'transactions': transactions,
    })
