from urllib.parse import urlencode
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction as db_transaction

from customers.models import Customer
from customers.views import _get_customer
from payments.models import Transaction
from payments.services import process_payment
from billing_app.invoice_generator import InvoiceGenerator
from .models import PaymentGateway
from .forms import GatewaySelectionForm
from . import services


@login_required
def gateway_select(request, context_key, context_value):
    customer = _get_customer(request.user)
    amount = float(request.GET.get('amount', 0))

    if request.method == 'POST':
        form = GatewaySelectionForm(request.POST)
        if form.is_valid():
            gateway_code = form.cleaned_data['gateway']
            phone = form.cleaned_data.get('phone', '')
            url = reverse('payment_gateways:process', kwargs={
                'gateway_code': gateway_code,
                'context_key': context_key,
                'context_value': context_value,
            })
            params = urlencode({'amount': amount, 'phone': phone})
            return redirect(f'{url}?{params}')
    else:
        form = GatewaySelectionForm()

    return render(request, 'payment_gateways/select.html', {
        'customer': customer,
        'form': form,
        'context_key': context_key,
        'context_value': context_value,
        'amount': amount,
    })


@login_required
def gateway_process(request, gateway_code, context_key, context_value):
    customer = _get_customer(request.user)
    gateway = get_object_or_404(PaymentGateway, code=gateway_code, is_active=True)

    amount = float(request.GET.get('amount', 0))
    phone = request.GET.get('phone', customer.phone)

    if amount <= 0:
        messages.error(request, 'Invalid payment amount.')
        return redirect('customers:dashboard')

    response = services.process_gateway_payment(gateway_code, amount, phone)

    with db_transaction.atomic():
        if context_key == 'recharge':
            txn = process_payment(
                customer_id=customer.pk,
                amount=amount,
                description=f'Recarga via {gateway.name}',
                gateway_code=gateway_code,
            )
        elif context_key == 'pay_invoice':
            from billing_app.models import Invoice
            invoice = get_object_or_404(Invoice, pk=int(context_value), customer=customer)
            remaining = float(invoice.amount - (invoice.paid_amount or 0))
            if amount > remaining:
                raise ValueError('Amount exceeds remaining balance')
            txn = process_payment(
                customer_id=customer.pk,
                amount=amount,
                payment_type='payment',
                invoice_id=invoice.pk,
                description=f'Pagamento fatura {invoice.invoice_number} via {gateway.name}',
                gateway_code=gateway_code,
            )
        else:
            txn = process_payment(
                customer_id=customer.pk,
                amount=amount,
                description=f'Pagamento via {gateway.name}',
                gateway_code=gateway_code,
            )

        gateway_status = 'success' if response['success'] else 'failed'
        services.create_gateway_transaction(
            gateway=gateway,
            transaction=txn,
            gateway_reference=response.get('reference', ''),
            status=gateway_status,
            response_data=response,
        )
        if not response['success']:
            txn.status = 'failed'
            txn.save(update_fields=['status'])

    return render(request, 'payment_gateways/result.html', {
        'customer': customer,
        'gateway': gateway,
        'transaction': txn,
        'response': response,
        'success': response['success'],
    })


@login_required
def gateway_list(request):
    gateways = services.get_active_gateways()
    return render(request, 'payment_gateways/list.html', {
        'gateways': gateways,
    })


@login_required
def download_receipt(request, transaction_id):
    customer = _get_customer(request.user)
    txn = get_object_or_404(Transaction, transaction_id=transaction_id, customer=customer)
    if txn.invoice:
        pdf = InvoiceGenerator.generate_payment_receipt(txn.invoice)
        filename = f'recibo_{txn.invoice.invoice_number}.pdf'
    else:
        pdf = InvoiceGenerator.generate_recharge_receipt(customer, float(txn.amount), txn.transaction_id)
        filename = f'recibo_{txn.transaction_id[:8]}.pdf'
    return HttpResponse(pdf.getvalue(), content_type='application/pdf',
                        headers={'Content-Disposition': f'attachment; filename="{filename}"'})
