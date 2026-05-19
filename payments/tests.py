from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from customers.models import Customer
from billing_app.models import Invoice
from .models import Transaction
from . import api_views
from .services import process_payment, pay_invoice, recharge_balance


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-001', current_balance=Decimal('100.00')
        )

    def test_transaction_creation(self):
        txn = Transaction.objects.create(
            customer=self.customer,
            transaction_id='TXN-TEST-001',
            transaction_type='payment',
            amount=Decimal('50.00'),
            status='completed',
        )
        self.assertEqual(txn.amount, Decimal('50.00'))
        self.assertEqual(txn.status, 'completed')
        self.assertIsNotNone(txn.created_at)

    def test_transaction_str(self):
        txn = Transaction.objects.create(
            customer=self.customer,
            transaction_id='TXN-STR-001',
            transaction_type='credit',
            amount=Decimal('25.00'),
        )
        self.assertIn('TXN-STR-001', str(txn))

    def test_pending_default(self):
        txn = Transaction.objects.create(
            customer=self.customer,
            transaction_id='TXN-DEF-001',
            transaction_type='payment',
            amount=Decimal('10.00'),
        )
        self.assertEqual(txn.status, 'pending')

    def test_all_types(self):
        for ttype in ['payment', 'credit', 'refund', 'adjustment']:
            txn = Transaction.objects.create(
                customer=self.customer,
                transaction_id=f'TXN-TYPE-{ttype}',
                transaction_type=ttype,
                amount=Decimal('10.00'),
            )
            self.assertEqual(txn.transaction_type, ttype)


class PaymentServicesTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-001',
            current_balance=Decimal('100.00'), debt=Decimal('0.00'),
        )
        self.invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-001',
            amount=Decimal('200.00'),
            issue_date='2026-01-01',
            due_date='2026-02-01',
            status='issued',
        )

    def test_process_payment_recharge(self):
        txn = process_payment(
            customer_id=self.customer.pk,
            amount=Decimal('50.00'),
            payment_type='payment',
            description='Test recharge',
        )
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('150.00'))
        self.assertEqual(txn.status, 'completed')
        self.assertIsNotNone(txn.transaction_id)

    def test_process_payment_invoice(self):
        txn = process_payment(
            customer_id=self.customer.pk,
            amount=Decimal('50.00'),
            payment_type='payment',
            invoice_id=self.invoice.pk,
            description='Test payment',
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.paid_amount, Decimal('50.00'))
        self.assertEqual(self.invoice.status, 'partially_paid')
        self.assertEqual(txn.status, 'completed')

    def test_pay_invoice_full(self):
        txn = pay_invoice(self.invoice.pk, Decimal('200.00'))
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.paid_amount, Decimal('200.00'))
        self.assertEqual(self.invoice.status, 'paid')
        self.assertEqual(txn.status, 'completed')

    def test_pay_invoice_already_paid(self):
        self.invoice.status = 'paid'
        self.invoice.paid_amount = Decimal('200.00')
        self.invoice.save()
        with self.assertRaises(ValueError):
            pay_invoice(self.invoice.pk, Decimal('50.00'))

    def test_recharge_balance(self):
        txn = recharge_balance(self.customer.pk, Decimal('30.00'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('130.00'))
        self.assertEqual(txn.status, 'completed')

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            process_payment(self.customer.pk, Decimal('0'), payment_type='payment')

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            process_payment(self.customer.pk, Decimal('-10'), payment_type='payment')

    def test_notifications_created(self):
        from notifications.models import Notification
        recharge_balance(self.customer.pk, Decimal('25.00'))
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().type, 'recharge')


class PaymentAPITest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-API-001',
            current_balance=Decimal('100.00'),
        )
        self.client.login(username='client1', password='pass123')

    def test_api_customer_list(self):
            response = self.client.get(reverse('api_customer_list'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 1)

    def test_api_recharge(self):
        response = self.client.post(
            reverse('api_recharge'),
            {'amount': '50.00'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('150.00'))

    def test_api_recharge_invalid(self):
        response = self.client.post(
            reverse('api_recharge'),
            {'amount': '0'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_api_unauthorized(self):
        self.client.logout()
        response = self.client.get(reverse('api_customer_list'))
        self.assertEqual(response.status_code, 403)
