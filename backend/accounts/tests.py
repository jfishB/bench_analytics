"""
- This file contains tests for the accounts module
- Covers:
    - domain/application services in `backend/accounts/services.py`
    - API views in `backend/accounts/views.py` wired via `backend/accounts/urls.py`
- Notation:
- 200 - HTTP_200_OK
- 201 - HTTP_201_CREATED
- 400 - HTTP_400_BAD_REQUEST
- 401 - HTTP_401_UNAUTHORIZED
- 500 - HTTP_500_INTERNAL_SERVER_ERROR
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from unittest.mock import patch
from django.urls import reverse

from .exceptions import EmailAlreadyExistsError, InvalidCredentialsError, MissingFieldsError, UserAlreadyExistsError
from .services import login_user, register_user


def test_smoke():
    """Simple smoke test to verify the accounts test module is discovered."""

    assert True


class AccountServiceTests(TestCase):
    """Unit tests for the accounts service layer (register_user, login_user)."""

    def setUp(self):
        # Create a sample user for login tests
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="test123"
        )

    # --- register_user tests ---

    def test_register_user_success(self):
        user = register_user("newuser", "new@example.com", "pass1234")
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")

    def test_register_user_missing_username(self):
        with self.assertRaises(MissingFieldsError):
            register_user("", "email@example.com", "password")

    def test_register_user_missing_email(self):
        with self.assertRaises(MissingFieldsError):
            register_user("user", "", "password")

    def test_register_user_missing_password(self):
        with self.assertRaises(MissingFieldsError):
            register_user("user", "email@example.com", "")

    def test_register_user_all_fields_missing(self):
        with self.assertRaises(MissingFieldsError):
            register_user("", "", "")

    def test_register_user_existing_username(self):
        with self.assertRaises(UserAlreadyExistsError):
            register_user("testuser", "other@example.com", "password")

    def test_register_user_existing_email(self):
        with self.assertRaises(EmailAlreadyExistsError):
            register_user("newuser2", "test@example.com", "password")

    def test_register_user_existing_username_and_email(self):
        # Both username and email already taken – should raise email error first
        with self.assertRaises(EmailAlreadyExistsError):
            register_user("testuser", "test@example.com", "password")

    # --- login_user tests ---

    def test_login_user_success(self):
        data = login_user("testuser", "test123")
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["user"]["username"], "testuser")
        self.assertEqual(data["user"]["email"], "test@example.com")

    def test_login_user_invalid_password(self):
        with self.assertRaises(InvalidCredentialsError):
            login_user("testuser", "wrongpassword")

    def test_login_user_unknown_username(self):
        with self.assertRaises(InvalidCredentialsError):
            login_user("unknown", "somepassword")

    def test_login_user_blank_username(self):
        with self.assertRaises(InvalidCredentialsError):
            login_user("", "test123")

    def test_login_user_blank_password(self):
        with self.assertRaises(InvalidCredentialsError):
            login_user("testuser", "")


class AccountViewTests(TestCase):
    """Integration tests for the accounts HTTP API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/v1/auth/register/"
        self.login_url = "/api/v1/auth/login/"
        self.protected_url = "/api/v1/auth/protected/"

        # Create a sample user for login tests
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="test123"
        )

    # --- register endpoint tests ---

    def test_register_api_success(self):
        data = {
            "username": "newuser", 
            "email": "new@example.com", 
            "password": "pass1234"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "User created successfully!")

    def test_register_api_missing_username(self):
        data = {
            "username": "", 
            "email": "new@example.com", 
            "password": "pass1234"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_api_missing_email(self):
        data = {
            "username": "newuser", 
            "email": "", 
            "password": "pass1234"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_api_missing_password(self):
        data = {
            "username": "newuser", 
            "email": "new@example.com", 
            "password": ""
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_api_existing_username(self):
        data = {
            "username": "testuser", 
            "email": "newemail@example.com", 
            "password": "pass123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_api_existing_email(self):
        data = {
            "username": "otheruser", 
            "email": "test@example.com", 
            "password": "pass123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    # --- login endpoint tests ---

    def test_login_api_success(self):
        data = {
            "username": "testuser", 
            "password": "test123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_api_invalid_password(self):
        data = {
            "username": "testuser", 
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.data)

    def test_login_api_unknown_username(self):
        data = {
            "username": "unknown", 
            "password": "somepassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.data)

    def test_login_api_missing_username(self):
        data = {
            "username": "", 
            "password": "test123"
        }
        response = self.client.post(self.login_url, data)
        # DRF / view should treat this as invalid credentials or bad request; expect 400 or 401
        self.assertIn(response.status_code, {400, 401})

    def test_login_api_missing_password(self):
        data = {
            "username": "testuser", 
            "password": ""
        }
        response = self.client.post(self.login_url, data)
        self.assertIn(response.status_code, {400, 401})

    # --- protected endpoint tests ---

    def test_protected_view_requires_auth(self):
        # No auth token provided / Unauthenticated request
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 401)

        # Authenticate using a JWT access token and retry
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertIn(self.user.username, response.data["message"])


class AccountExceptionTests(TestCase):
    """Tests view-layer error handling for domain and unexpected exceptions.

    Mocks service-layer functions to ensure the views map DomainError subclasses
    to appropriate HTTP responses and that unexpected exceptions result in 500.
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/v1/auth/register/"
        self.login_url = "/api/v1/auth/login/"
        self.logout_url = "/api/v1/auth/logout/"

        # Create a sample user for login tests
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="test123"
        )

    def test_register_view_handles_domain_error(self):
        with patch("accounts.views.register_user") as mock_register:
            mock_register.side_effect = UserAlreadyExistsError("username")

            data = {
                "username": "testuser", 
                "email": "new@example.com", 
                "password": "pass"
            }

            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.data)

    def test_register_view_handles_unexpected_exception(self):
        with patch("accounts.views.register_user") as mock_register:
            mock_register.side_effect = Exception("boom")

            data = {
                "username": "newuser", 
                "email": "new@example.com", 
                "password": "pass"
            }

            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.data)

    def test_login_view_handles_unexpected_exception(self):
        with patch("accounts.views.login_user") as mock_login:
            mock_login.side_effect = Exception("boom")

            response = self.client.post(reverse("accounts:login"), {
                "username": "newuser",
                "password": "pass"
            })

            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.data)

    def test_login_view_handles_domain_error(self):
        with patch("accounts.views.login_user") as mock_login:
            mock_login.side_effect = InvalidCredentialsError("bad")

            data = {
                "username": "testuser", 
                "password": "wrong"
            }
            
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 401)
            self.assertIn("error", response.data)

    def test_logout_missing_refresh_returns_400(self):
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # No refresh field -> 400
        response = self.client.post(self.logout_url, data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_logout_successful(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(self.logout_url, data={"refresh": str(refresh)})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Logout successful.")

    def test_logout_invalid_token_returns_400(self):
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Patch RefreshToken constructor to raise TokenError
        with patch("accounts.views.RefreshToken") as mock_refresh:
            mock_refresh.side_effect = TokenError("invalid")

            response = self.client.post(self.logout_url, data={"refresh": "bad"})
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.data)

    def test_logout_unexpected_exception_returns_500(self):
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        with patch("accounts.views.RefreshToken") as mock_refresh:
            mock_refresh.side_effect = Exception("boom")

            response = self.client.post(self.logout_url, data={"refresh": "anything"})
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.data)
