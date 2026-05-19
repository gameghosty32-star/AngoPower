from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from .models import Notification


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')

    def test_notification_creation(self):
        notif = Notification.objects.create(
            user=self.user,
            type='recharge',
            title='Recharge Confirmed',
            message='Your recharge of $50.00 was successful.',
        )
        self.assertEqual(notif.title, 'Recharge Confirmed')
        self.assertFalse(notif.is_read)
        self.assertIsNotNone(notif.created_at)

    def test_notification_str(self):
        notif = Notification.objects.create(
            user=self.user, type='system', title='System Update', message='System maintenance',
        )
        self.assertEqual(str(notif), '[System Notification] System Update')

    def test_notification_is_read_default(self):
        notif = Notification.objects.create(
            user=self.user, type='payment', title='Payment', message='Paid',
        )
        self.assertFalse(notif.is_read)

    def test_notification_mark_read(self):
        notif = Notification.objects.create(
            user=self.user, type='invoice', title='Invoice Alert', message='Due soon',
        )
        notif.is_read = True
        notif.save()
        self.assertTrue(notif.is_read)

    def test_all_types(self):
        for ntype in ['recharge', 'invoice', 'ticket', 'payment', 'system']:
            Notification.objects.create(
                user=self.user, type=ntype, title='Test', message='Test msg',
            )
        self.assertEqual(Notification.objects.count(), 5)


class NotificationViewsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='client1', password='pass123')
        self.notif = Notification.objects.create(
            user=self.user, type='recharge',
            title='Recharge Confirmed',
            message='$50.00 added',
        )
        self.client.login(username='client1', password='pass123')

    def test_notification_list_view(self):
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/list.html')
        self.assertContains(response, 'Recharge Confirmed')

    def test_mark_read_view(self):
        self.assertFalse(self.notif.is_read)
        response = self.client.get(reverse('notifications:mark_read', args=[self.notif.pk]))
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

    def test_mark_read_other_user(self):
        user2 = CustomUser.objects.create_user(username='other', password='pass123')
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('notifications:mark_read', args=[self.notif.pk]))
        self.assertEqual(response.status_code, 404)

    def test_mark_all_read_view(self):
        Notification.objects.create(
            user=self.user, type='payment', title='Payment', message='Done'
        )
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 2)
        response = self.client.get(reverse('notifications:mark_all_read'))
        self.assertRedirects(response, reverse('notifications:list'))
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_no_notifications(self):
        Notification.objects.all().delete()
        response = self.client.get(reverse('notifications:list'))
        self.assertContains(response, 'Nenhuma notificação')

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 302)
