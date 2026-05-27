from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from .models import Customer


class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='client1', password='pass123', user_type='client'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            meter_number='MTR-001',
            customer_type='prepaid',
            current_balance=Decimal('100.00'),
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.meter_number, 'MTR-001')
        self.assertEqual(self.customer.current_balance, Decimal('100.00'))
        self.assertEqual(self.customer.customer_type, 'prepaid')

    def test_customer_str(self):
        self.assertEqual(str(self.customer), 'client1 - MTR-001')

    def test_customer_defaults(self):
        user2 = CustomUser.objects.create_user(username='client2', password='pass123')
        c2 = Customer.objects.create(user=user2, meter_number='MTR-002')
        self.assertEqual(c2.current_balance, Decimal('0.00'))
        self.assertEqual(c2.debt, Decimal('0.00'))
        self.assertEqual(c2.customer_type, 'prepaid')
        self.assertEqual(c2.phone, '')
        self.assertEqual(c2.address, '')

    def test_postpaid_customer(self):
        user3 = CustomUser.objects.create_user(username='client3', password='pass123')
        c3 = Customer.objects.create(
            user=user3, meter_number='MTR-003', customer_type='postpaid'
        )
        self.assertEqual(c3.customer_type, 'postpaid')

    def test_unique_meter_number(self):
        with self.assertRaises(Exception):
            Customer.objects.create(
                user=CustomUser.objects.create_user(username='dup', password='pass123'),
                meter_number='MTR-001',
            )


class CustomerViewsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='client1', password='pass123', user_type='client'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            meter_number='MTR-001',
            current_balance=Decimal('100.00'),
            debt=Decimal('10.00'),
        )
        self.client.login(username='client1', password='pass123')

    def test_dashboard_redirects_prepaid(self):
        response = self.client.get(reverse('customers:dashboard'))
        self.assertRedirects(response, reverse('prepaid:dashboard'))

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('customers:dashboard'))
        self.assertRedirects(response, f'/login/?next={reverse("customers:dashboard")}')

    def test_balance_redirects_prepaid(self):
        response = self.client.get(reverse('customers:balance'))
        self.assertRedirects(response, reverse('prepaid:balance'))

    def test_prepaid_dashboard(self):
        response = self.client.get(reverse('prepaid:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepaid/dashboard.html')
        self.assertContains(response, 'MTR-001')
        self.assertContains(response, '100.00')

    def test_prepaid_balance_view(self):
        response = self.client.get(reverse('prepaid:balance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepaid/balance.html')
        self.assertContains(response, '100')

    def test_prepaid_dashboard(self):
        response = self.client.get(reverse('prepaid:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepaid/dashboard.html')
        self.assertContains(response, 'MTR-001')
        self.assertContains(response, 'Saldo Atual')

    def test_prepaid_recharge_view_get(self):
        response = self.client.get(reverse('prepaid:recharge'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepaid/recharge.html')

    def test_prepaid_recharge_view_post(self):
        response = self.client.post(reverse('prepaid:recharge'), {'amount': '50.00'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/gateways/select/recharge/', response.url)

    def test_prepaid_recharge_invalid_amount(self):
        response = self.client.post(reverse('prepaid:recharge'), {'amount': '0'})
        self.assertEqual(response.status_code, 200)

    def test_prepaid_transaction_history_view(self):
        response = self.client.get(reverse('prepaid:transactions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepaid/transaction_history.html')

    def test_no_profile_redirect_creates_customer(self):
        self.client.logout()
        user2 = CustomUser.objects.create_user(
            username='noprofile', password='pass123', user_type='client'
        )
        self.client.login(username='noprofile', password='pass123')
        response = self.client.get(reverse('customers:dashboard'))
        self.assertRedirects(response, reverse('prepaid:dashboard'))
        self.assertTrue(Customer.objects.filter(user=user2).exists())
