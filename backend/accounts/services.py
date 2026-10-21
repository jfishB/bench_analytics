"""
- This file implements the domain/application services for user accounts
- Imported by:
    - backend/accounts/views.py
usage:
    - `register_user` is used by the register view to create a new user
    - `login_user` is used by the login view to authenticate and issue tokens
"""

import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import (
    EmailAlreadyExistsError, InvalidCredentialsError,
    MissingFieldsError, UserAlreadyExistsError, UserConflictError
)

logger = logging.getLogger(__name__)


DEMO_USERNAME = "demo"


def demo_login() -> dict:
    """
    Logs in the shared demo account, creating it on first use, so visitors
    can explore the app without registering.

    Also seeds the sample roster if the database is still empty, so the
    optimizer has players to work with on a fresh deployment.
    """
    # Imported here to keep accounts decoupled from roster at import time.
    from roster.services.sample_data_loader import load_sample_players

    user, _ = User.objects.get_or_create(
        username=DEMO_USERNAME,
        defaults={"email": "demo@benchanalytics.local"},
    )

    result = load_sample_players()
    if not result.get("success"):
        # The demo still works for anything that does not need a roster.
        logger.warning("Demo roster seeding failed: %s", result.get("error"))

    return _tokens_for(user)


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

    try:  # To handle race conditions where several similar users are trying
        # to be created within a short time frame
        user = User.objects.create_user(username=username, email=email,
                                        password=password)

        return user

    except IntegrityError:
        raise UserConflictError("Username conflict due to parallel request.")


def login_user(username, password) -> dict:
    """
    Handles user authentication and token generation.
    Returns JWT tokens if successful.
    """

    user = authenticate(username=username, password=password)

    if user is None:
        raise InvalidCredentialsError("Invalid credentials.")

    return _tokens_for(user)


def _tokens_for(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }
