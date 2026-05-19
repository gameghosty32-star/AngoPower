from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from customers.models import Customer
from .models import Invoice


class InvoiceModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='client1', password='pass123', user_type='client'
        )
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-001', customer_type='postpaid'
        )

    def test_invoice_creation(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-001',
            amount=Decimal('150.00'),
            issue_date='2026-01-01',
            due_date='2026-01-31',
            status='issued',
        )
        self.assertEqual(invoice.invoice_number, 'INV-001')
        self.assertEqual(invoice.amount, Decimal('150.00'))
        self.assertEqual(invoice.status, 'issued')
        self.assertEqual(invoice.paid_amount, Decimal('0.00'))

    def test_invoice_str(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-001',
            amount=Decimal('100.00'),
            issue_date='2026-01-01',
            due_date='2026-01-31',
        )
        self.assertIn('INV-001', str(invoice))

    def test_paid_invoice_flow(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-002',
            amount=Decimal('100.00'),
            issue_date='2026-01-01',
            due_date='2026-01-31',
            status='issued',
        )
        invoice.paid_amount = Decimal('100.00')
        invoice.status = 'paid'
        invoice.save()
        self.assertEqual(invoice.status, 'paid')

    def test_overdue_invoice(self):
        Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-003',
            amount=Decimal('200.00'),
            issue_date='2025-01-01',
            due_date='2025-02-01',
            status='overdue',
        )
        overdue = Invoice.objects.filter(status='overdue').count()
        self.assertEqual(overdue, 1)

    def test_partial_payment(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-004',
            amount=Decimal('100.00'),
            issue_date='2026-01-01',
            due_date='2026-01-31',
            status='issued',
        )
        invoice.paid_amount = Decimal('50.00')
        invoice.status = 'partially_paid'
        invoice.save()
        self.assertEqual(invoice.status, 'partially_paid')


class InvoiceViewsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='client1', password='pass123', user_type='client'
        )
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-001', customer_type='postpaid'
        )
        self.invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number='INV-001',
            amount=Decimal('100.00'),
            issue_date='2026-01-01',
            due_date='2026-02-01',
            status='issued',
        )
        self.client.login(username='client1', password='pass123')

    def test_invoice_list_view(self):
        response = self.client.get(reverse('billing:invoice_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/invoice_list.html')
        self.assertContains(response, 'INV-001')

    def test_invoice_detail_view(self):
        response = self.client.get(reverse('billing:invoice_detail', args=[self.invoice.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/invoice_detail.html')
        self.assertContains(response, 'INV-001')
        self.assertContains(response, '100.00')

    def test_invoice_detail_other_user(self):
        user2 = CustomUser.objects.create_user(username='other', password='pass123')
        Customer.objects.create(user=user2, meter_number='MTR-999')
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('billing:invoice_detail', args=[self.invoice.pk]))
        self.assertEqual(response.status_code, 404)

    def test_pay_invoice_view_get(self):
        response = self.client.get(reverse('billing:pay_invoice', args=[self.invoice.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/pay_invoice.html')

    def test_pay_invoice_view_post(self):
        response = self.client.post(
            reverse('billing:pay_invoice', args=[self.invoice.pk]),
            {'amount': '50.00'},
        )
        self.assertRedirects(response, reverse('billing:invoice_detail', args=[self.invoice.pk]))
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.paid_amount, Decimal('50.00'))

    def test_consumption_view(self):
        response = self.client.get(reverse('billing:consumption'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing/consumption_history.html')

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('billing:invoice_list'))
        self.assertEqual(response.status_code, 302)
