from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    MissingFieldsError,
    UserAlreadyExistsError,
)
from .services import login_user, register_user

# Create your tests here.


def test_smoke():
    assert True


# To test via terminal:
# 1. follow steps as if you are about to run backend but dont run server (you should be in a venv)
# 2. cd backend
# 3. python manage.py test accounts
# If error occurs when command is run try this command: pip install djangorestframework-simplejwt


# Unit tests for services.py
# To test this class specifically: python manage.py test accounts.tests.AccountServiceTests
class AccountServiceTests(TestCase):
    def setUp(self):
        # Create a sample user for login tests
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="test123")

    def test_register_user_success(self):
        user = register_user("newuser", "new@example.com", "pass1234")
        self.assertEqual(user.username, "newuser")

    def test_register_user_missing_fields(self):
        with self.assertRaises(MissingFieldsError):
            register_user("", "email@example.com", "password")

    def test_register_user_existing_username(self):
        with self.assertRaises(UserAlreadyExistsError):
            register_user("testuser", "other@example.com", "password")

    def test_register_user_existing_email(self):
        with self.assertRaises(EmailAlreadyExistsError):
            register_user("newuser2", "test@example.com", "password")

    def test_login_user_success(self):
        data = login_user("testuser", "test123")
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["username"], "testuser")

    def test_login_user_invalid_credentials(self):
        with self.assertRaises(InvalidCredentialsError):
            login_user("testuser", "wrongpassword")


# Integration tests for views.py
# To test this class specifically: python manage.py test accounts.tests.AccountViewTests
class AccountViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/v1/auth/register/"
        self.login_url = "/api/v1/auth/login/"
        self.protected_url = "/api/v1/auth/protected/"

        # Create a sample user for login tests
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="test123")

    def test_register_api_success(self):
        data = {"username": "newuser", "email": "new@example.com", "password": "pass1234"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User created successfully!")

    def test_register_api_existing_username(self):
        data = {"username": "testuser", "email": "newemail@example.com", "password": "pass123"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_api_success(self):
        data = {"username": "testuser", "password": "test123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_api_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_protected_view_requires_auth(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
