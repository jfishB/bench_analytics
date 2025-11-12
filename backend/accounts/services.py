from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    MissingFieldsError,
    UserAlreadyExistsError,
)


def register_user(username, email, password) -> User:
    """
    Handles user registration logic.
    """

    if not all([username, email, password]):
        raise MissingFieldsError("Username, email, and password are required.")

    if User.objects.filter(username=username).exists():
        raise UserAlreadyExistsError("Username already exists.")

    if User.objects.filter(email=email).exists():
        raise EmailAlreadyExistsError("Email already exists.")

    try:  # To handle cases where several of a similar user is trying to be created within a short time frame
        user = User.objects.create_user(username=username, email=email, password=password)

        return user

    except IntegrityError:
        raise UserAlreadyExistsError("Username already exists.")


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
        # "username": user.username,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }
