from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from customers.models import Customer
from .models import Category, Ticket, Message


class SupportModelsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-001'
        )
        self.category = Category.objects.create(name='Billing', description='Billing issues')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Billing')
        self.assertEqual(str(self.category), 'Billing')

    def test_ticket_creation(self):
        ticket = Ticket.objects.create(
            customer=self.customer,
            subject='High bill',
            description='My bill is too high',
            priority='high',
            category=self.category,
        )
        self.assertEqual(ticket.subject, 'High bill')
        self.assertEqual(ticket.priority, 'high')
        self.assertEqual(ticket.status, 'open')
        self.assertIsNone(ticket.assigned_to)

    def test_ticket_str(self):
        ticket = Ticket.objects.create(
            customer=self.customer,
            subject='Test ticket',
            description='Testing',
        )
        self.assertIn('Test ticket', str(ticket))
        self.assertIn('MTR-001', str(ticket))

    def test_default_priority(self):
        ticket = Ticket.objects.create(
            customer=self.customer, subject='Default', description='Desc'
        )
        self.assertEqual(ticket.priority, 'medium')

    def test_message_creation(self):
        ticket = Ticket.objects.create(
            customer=self.customer, subject='Test', description='Desc'
        )
        msg = Message.objects.create(
            ticket=ticket,
            author=self.user,
            content='This is a test message',
        )
        self.assertEqual(msg.content, 'This is a test message')
        self.assertEqual(str(msg), f'Message by client1 on Ticket #{ticket.pk}')

    def test_message_ordering(self):
        ticket = Ticket.objects.create(
            customer=self.customer, subject='Order test', description='Desc'
        )
        m1 = Message.objects.create(ticket=ticket, author=self.user, content='First')
        m2 = Message.objects.create(ticket=ticket, author=self.user, content='Second')
        messages = ticket.messages.all()
        self.assertEqual(messages[0].content, 'First')
        self.assertEqual(messages[1].content, 'Second')


class SupportViewsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')
        self.customer = Customer.objects.create(
            user=self.user, meter_number='MTR-001'
        )
        self.category = Category.objects.create(name='Technical')
        self.ticket = Ticket.objects.create(
            customer=self.customer,
            subject='Internet problem',
            description='No connectivity',
            category=self.category,
        )
        self.client.login(username='client1', password='pass123')

    def test_ticket_list_view(self):
        response = self.client.get(reverse('support:ticket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/ticket_list.html')
        self.assertContains(response, 'Internet problem')

    def test_ticket_create_view_get(self):
        response = self.client.get(reverse('support:ticket_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/ticket_create.html')

    def test_ticket_create_view_post(self):
        response = self.client.post(
            reverse('support:ticket_create'),
            {
                'subject': 'New issue',
                'description': 'Description of new issue',
                'category': self.category.pk,
                'priority': 'high',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ticket.objects.filter(subject='New issue').exists())

    def test_ticket_detail_view(self):
        response = self.client.get(reverse('support:ticket_detail', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support/ticket_detail.html')

    def test_ticket_detail_add_message(self):
        response = self.client.post(
            reverse('support:ticket_detail', args=[self.ticket.pk]),
            {'content': 'Need help ASAP'},
        )
        self.assertRedirects(response, reverse('support:ticket_detail', args=[self.ticket.pk]))
        self.assertEqual(self.ticket.messages.count(), 1)
        self.assertEqual(self.ticket.messages.first().content, 'Need help ASAP')

    def test_ticket_detail_other_user(self):
        user2 = CustomUser.objects.create_user(username='other', password='pass123')
        Customer.objects.create(user=user2, meter_number='MTR-999')
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('support:ticket_detail', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 404)

    def test_create_ticket_empty_subject(self):
        response = self.client.post(
            reverse('support:ticket_create'),
            {'subject': '', 'description': 'Desc'},
        )
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('support:ticket_list'))
        self.assertEqual(response.status_code, 302)
