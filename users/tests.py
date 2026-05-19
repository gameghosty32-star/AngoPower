from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepass123',
            user_type='client',
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.user_type, 'client')

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser (Client)')

    def test_default_user_type(self):
        user = CustomUser.objects.create_user(username='defaultuser', password='pass123')
        self.assertEqual(user.user_type, 'client')

    def test_operator_user(self):
        user = CustomUser.objects.create_user(
            username='operator1', password='pass123', user_type='operator'
        )
        self.assertEqual(user.user_type, 'operator')

    def test_admin_user(self):
        user = CustomUser.objects.create_user(
            username='admin1', password='pass123', user_type='admin'
        )
        self.assertEqual(user.user_type, 'admin')
        self.assertTrue(user.user_type in ['client', 'operator', 'admin'])


class RegisterViewTest(TestCase):
    def test_register_page_status(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_success(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('customers:dashboard'))
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        CustomUser.objects.create_user(username='existing', password='pass12345')
        data = {
            'username': 'existing',
            'email': 'dup@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
