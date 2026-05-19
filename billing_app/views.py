from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from customers.models import Customer
from .models import Invoice
from payments.models import Transaction
from payments.services import pay_invoice


def _get_customer(user):
    return get_object_or_404(Customer, user=user)


@login_required
def invoice_list(request):
    customer = _get_customer(request.user)
    invoices = customer.invoices.all()
    return render(request, 'billing/invoice_list.html', {
        'customer': customer,
        'invoices': invoices,
    })


@login_required
def invoice_detail(request, pk):
    customer = _get_customer(request.user)
    invoice = get_object_or_404(
        Invoice.objects.prefetch_related('transactions'),
        pk=pk, customer=customer,
    )
    transactions = invoice.transactions.all()
    remaining = float(invoice.amount - (invoice.paid_amount or 0))
    return render(request, 'billing/invoice_detail.html', {
        'customer': customer,
        'invoice': invoice,
        'transactions': transactions,
        'remaining': remaining,
    })


@login_required
def pay_invoice_view(request, pk):
    customer = _get_customer(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, customer=customer)
    remaining = float(invoice.amount - (invoice.paid_amount or 0))
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            if amount <= 0:
                raise ValueError('Amount must be positive')
            if amount > remaining:
                raise ValueError('Amount exceeds remaining balance')
            pay_invoice(invoice.pk, amount)
            messages.success(request, f'Payment of ${amount:.2f} for invoice {invoice.invoice_number} successful!')
            return redirect('billing:invoice_detail', pk=invoice.pk)
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
    return render(request, 'billing/pay_invoice.html', {
        'customer': customer,
        'invoice': invoice,
        'remaining': remaining,
    })


@login_required
def consumption_history(request):
    customer = _get_customer(request.user)
    transactions = customer.transactions.filter(
        transaction_type__in=['payment', 'credit']
    ).order_by('-created_at')
    total = sum(float(t.amount) for t in transactions)
    avg_monthly = total / max(len(transactions), 1)
    return render(request, 'billing/consumption_history.html', {
        'customer': customer,
        'transactions': transactions,
        'total_consumption': total,
        'avg_monthly': round(avg_monthly, 2),
    })
