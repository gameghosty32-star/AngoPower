import uuid
from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone
from django.conf import settings

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


def _generate_invoice_documents(txn, invoice, customer, payment_type):
    try:
        from billing_app.invoice_generator import InvoiceGenerator
        if invoice:
            if txn.status == 'completed':
                pdf = InvoiceGenerator.generate_payment_receipt(invoice)
                InvoiceGenerator.create_notification(
                    invoice, 'payment',
                    f'Recibo - Fatura {invoice.invoice_number}',
                    f'Pagamento de {txn.amount}Kz confirmado para fatura {invoice.invoice_number}.',
                    link=f'/billing/{invoice.pk}/',
                )
                if customer.user.email:
                    InvoiceGenerator.send_email(
                        invoice, customer.user.email, pdf,
                        subject=f'Recibo de Pagamento - Fatura {invoice.invoice_number}',
                    )
        else:
            from billing_app.invoice_generator import InvoiceGenerator
            pdf = InvoiceGenerator.generate_recharge_receipt(customer, txn.amount, txn.transaction_id)
            InvoiceGenerator.create_notification(
                txn, 'recharge',
                'Recibo de Recarga',
                f'Recarga de {txn.amount}Kz confirmada. Saldo actual: {customer.current_balance}Kz.',
                link='/customers/transactions/',
            )
            if customer.user.email:
                invoice_placeholder = type('obj', (object,), {
                    'invoice_number': f'RCP-{txn.transaction_id[:8]}',
                    'customer': customer,
                    'amount': txn.amount,
                    'paid_amount': txn.amount,
                    'status': 'paid',
                    'updated_at': txn.created_at,
                })()
                InvoiceGenerator.send_email(
                    invoice_placeholder, customer.user.email, pdf,
                    subject=f'Recibo de Recarga - {txn.transaction_id[:8]}',
                )
    except Exception:
        pass


def process_payment(customer_id, amount, payment_type='payment', invoice_id=None, description='', gateway_code=None):
    amount = Decimal(str(amount))
    with db_transaction.atomic():
        customer = Customer.objects.select_for_update().get(pk=customer_id)

        if amount <= 0:
            raise ValueError('Amount must be positive')

        if gateway_code:
            description = f"{description} [{gateway_code}]"

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
            message=f"Transaction {transaction_id}: {amount:.2f}Kz - {description or payment_type}",
            link='/customers/transactions/',
        )

        invoice_obj = invoice if invoice_id else None
        _generate_invoice_documents(txn, invoice_obj, customer, payment_type)

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
