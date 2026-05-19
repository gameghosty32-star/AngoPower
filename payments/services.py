import uuid
from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone

from customers.models import Customer
from billing_app.models import Invoice
from .models import Transaction
from notifications.models import Notification


def _create_notification(user, ntype, title, message, link=''):
    Notification.objects.create(
        user=user,
        type=ntype,
        title=title,
        message=message,
        link=link,
    )


def process_payment(customer_id, amount, payment_type='payment', invoice_id=None, description=''):
    amount = Decimal(str(amount))
    with db_transaction.atomic():
        customer = Customer.objects.select_for_update().get(pk=customer_id)

        if amount <= 0:
            raise ValueError('Amount must be positive')

        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        txn = Transaction.objects.create(
            customer=customer,
            invoice_id=invoice_id,
            transaction_id=transaction_id,
            transaction_type=payment_type,
            amount=amount,
            status='completed',
            description=description,
        )

        if payment_type == 'payment':
            if invoice_id:
                invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
                invoice.paid_amount = (invoice.paid_amount or Decimal('0.00')) + amount
                if invoice.paid_amount >= invoice.amount:
                    invoice.status = 'paid'
                elif invoice.paid_amount > 0:
                    invoice.status = 'partially_paid'
                invoice.save()
            else:
                customer.current_balance += amount
                customer.save()
        elif payment_type == 'refund':
            if invoice_id:
                invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
                invoice.paid_amount -= amount
                if invoice.paid_amount < 0:
                    invoice.paid_amount = Decimal('0.00')
                invoice.save()
            else:
                customer.current_balance -= amount
                customer.save()

        notif_type = 'payment' if invoice_id else 'recharge'
        notif_title = 'Payment Confirmed' if invoice_id else 'Recharge Confirmed'
        _create_notification(
            user=customer.user,
            ntype=notif_type,
            title=notif_title,
            message=f"Transaction {transaction_id}: ${amount:.2f} - {description or payment_type}",
            link='/customers/transactions/',
        )

        return txn


def pay_invoice(invoice_id, amount):
    invoice = Invoice.objects.select_related('customer').get(pk=invoice_id)
    if invoice.status == 'paid':
        raise ValueError('Invoice already paid')
    return process_payment(
        customer_id=invoice.customer.pk,
        amount=amount,
        payment_type='payment',
        invoice_id=invoice_id,
        description=f"Payment for invoice {invoice.invoice_number}",
    )


def recharge_balance(customer_id, amount):
    return process_payment(
        customer_id=customer_id,
        amount=amount,
        payment_type='payment',
        description='Prepaid recharge',
    )
