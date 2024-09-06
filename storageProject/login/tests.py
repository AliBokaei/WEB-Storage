from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import EmailOrUsernameAuthenticationForm


class EmailOrUsernameAuthenticationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com',
                                             password='testpassword123')

    def test_invalid_login(self):
        form_data = {'username': 'wronguser', 'password': 'wrongpassword'}
        form = EmailOrUsernameAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'], ['Invalid login credentials'])

    def test_blank_username(self):
        form_data = {'username': '', 'password': 'testpassword123'}
        form = EmailOrUsernameAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_blank_password(self):
        form_data = {'username': 'testuser', 'password': ''}
        form = EmailOrUsernameAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
