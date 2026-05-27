from decimal import Decimal

from django.db import transaction as db_transaction

from customers.models import Customer
from payments.models import Transaction
from payments.services import process_payment


def get_balance(customer_id):
    customer = Customer.objects.get(pk=customer_id)
    return customer.current_balance


def recharge_customer(customer_id, amount):
    return process_payment(
        customer_id=customer_id,
        amount=Decimal(str(amount)),
        payment_type='payment',
        description='Prepaid recharge',
    )


def get_transaction_history(customer_id, limit=None):
    qs = Transaction.objects.filter(customer_id=customer_id).order_by('-created_at')
    if limit:
        qs = qs[:limit]
    return qs


def deduct_consumption(customer_id, amount):
    amount = Decimal(str(amount))
    with db_transaction.atomic():
        customer = Customer.objects.select_for_update().get(pk=customer_id)
        if customer.current_balance < amount:
            raise ValueError('Insufficient balance')
        customer.current_balance -= amount
        customer.save()
        return customer.current_balance
