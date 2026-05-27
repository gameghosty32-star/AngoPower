from decimal import Decimal

from django.utils import timezone

from customers.models import Customer
from billing_app.models import Invoice
from payments.models import Transaction
from payments.services import process_payment
from .models import PostpaidContract


def get_outstanding_invoices(customer_id):
    return Invoice.objects.filter(
        customer_id=customer_id,
    ).exclude(status='paid').order_by('due_date')


def pay_invoice_amount(invoice_id, amount):
    return process_payment(
        customer_id=Invoice.objects.get(pk=invoice_id).customer_id,
        amount=Decimal(str(amount)),
        payment_type='payment',
        invoice_id=invoice_id,
        description=f"Payment for invoice {Invoice.objects.get(pk=invoice_id).invoice_number}",
    )


def get_consumption_data(customer_id):
    transactions = Transaction.objects.filter(
        customer_id=customer_id,
        transaction_type__in=['payment', 'credit'],
    ).order_by('-created_at')
    total = sum(float(t.amount) for t in transactions)
    avg_monthly = total / max(len(transactions), 1)
    return {
        'transactions': transactions,
        'total': total,
        'avg_monthly': round(avg_monthly, 2),
    }


def calculate_debt(customer_id):
    invoices = Invoice.objects.filter(
        customer_id=customer_id,
        status__in=['issued', 'overdue', 'partially_paid'],
    )
    total_due = sum(float(i.amount - (i.paid_amount or 0)) for i in invoices)
    return total_due


APPLIANCE_BASE_VALUES = {
    'fridge': 5000,
    'ac': 8000,
    'tv': 2000,
    'microwave': 3000,
    'washing_machine': 4000,
}


def calculate_suggested_amount(appliances, is_commercial=False):
    total = sum(APPLIANCE_BASE_VALUES.get(a, 0) for a in appliances)
    if is_commercial:
        total = int(total * 1.5)
    return total


def create_contract(customer, activation_method, appliances=None, is_commercial=False, inspection_notes=''):
    contract, created = PostpaidContract.objects.get_or_create(
        customer=customer,
        defaults={
            'activation_method': activation_method,
            'appliances': appliances or [],
            'is_commercial': is_commercial,
            'inspection_notes': inspection_notes,
            'status': 'pending_inspection' if activation_method == 'inspection' else 'pending_approval',
        },
    )
    if not created:
        contract.activation_method = activation_method
        contract.appliances = appliances or []
        contract.is_commercial = is_commercial
        contract.inspection_notes = inspection_notes
        contract.status = 'pending_inspection' if activation_method == 'inspection' else 'pending_approval'
        contract.save()
    if activation_method == 'system_suggestion':
        contract.monthly_amount = calculate_suggested_amount(appliances or [], is_commercial)
        contract.save()
    return contract


def approve_contract(contract_id, admin_notes=''):
    contract = PostpaidContract.objects.get(pk=contract_id)
    contract.status = 'active'
    contract.admin_approval_notes = admin_notes
    contract.approved_at = timezone.now()
    contract.save()
    return contract


def reject_contract(contract_id, admin_notes=''):
    contract = PostpaidContract.objects.get(pk=contract_id)
    contract.status = 'rejected'
    contract.admin_approval_notes = admin_notes
    contract.save()
    return contract


def get_pending_contracts():
    return PostpaidContract.objects.filter(status__in=['pending_inspection', 'pending_approval']).select_related('customer__user')
