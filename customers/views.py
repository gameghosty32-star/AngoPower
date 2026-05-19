from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Customer
from payments.models import Transaction
from payments.services import recharge_balance


def _get_customer(user):
    return get_object_or_404(Customer, user=user)


@login_required
def dashboard(request):
    try:
        customer = _get_customer(request.user)
    except:
        return render(request, 'customers/no_profile.html')

    recent_transactions = customer.transactions.order_by('-created_at')[:5]
    return render(request, 'customers/dashboard.html', {
        'customer': customer,
        'recent_transactions': recent_transactions,
    })


@login_required
def check_balance(request):
    customer = _get_customer(request.user)
    return render(request, 'customers/balance.html', {
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
            recharge_balance(customer.pk, amount)
            messages.success(request, f'Recharge of ${amount:.2f} successful!')
            return redirect('customers:balance')
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
    return render(request, 'customers/recharge.html', {
        'customer': customer,
    })


@login_required
def transaction_history(request):
    customer = _get_customer(request.user)
    transactions = customer.transactions.all()
    return render(request, 'customers/transaction_history.html', {
        'customer': customer,
        'transactions': transactions,
    })
