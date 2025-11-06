from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import (
    UserAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    MissingFieldsError,
)

def register_user(username, email, password) -> User:
    """
    Handles user registration logic.
    """

    if not username or not email or not password:
        raise MissingFieldsError("All fields are required.")

    if User.objects.filter(username=username).exists():
        raise UserAlreadyExistsError("Username already exists.")

    if User.objects.filter(email=email).exists():
        raise EmailAlreadyExistsError("Email already exists.")

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    return user


def login_user(username, password) -> dict:
    """
    Handles user authentication and token generation.
    Returns JWT tokens if successful.
    """

    user = authenticate(username=username, password=password)

    if user is None:
        raise InvalidCredentialsError("Invalid credentials.")

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
    }