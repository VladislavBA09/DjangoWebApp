from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import User
from uuid import uuid4

class RegistrationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_get_registration_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')

    def test_post_registration_success(self):
        with patch('app.views.send_email') as mock_send_email:
            response = self.client.post(self.url, {
                'email': 'test@example.com',
                'password': 'securePassword123',
                'confirm_password': 'securePassword123'
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'registration_done.html')
            self.assertTrue(User.objects.filter(email='test@example.com').exists())
            mock_send_email.assert_called_once()

    def test_post_password_mismatch(self):
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'password': 'password1',
            'confirm_password': 'password2'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The passwords do not match')

    def test_post_invalid_email(self):
        response = self.client.post(self.url, {
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email must contain the "@" symbol.')


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login_user')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='securePassword123',
            confirmation=True
        )

    def test_login_success(self):
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'password': 'securePassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_unverified_user(self):
        self.user.confirmation = False
        self.user.save()
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'password': 'securePassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User profile not verified')

    def test_login_invalid_password(self):
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'password': 'wrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect password')
