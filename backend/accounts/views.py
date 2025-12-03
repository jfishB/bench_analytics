"""
- This file defines the HTTP API endpoints for the accounts module.
"""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .exceptions import DomainError
from .services import login_user, register_user

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello, {request.user.username}!"})


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Handles user registration requests.
    """
    try:
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        user = register_user(username, email, password)

        return Response(
            {"message": "User created successfully!", "username":
             user.username},
            status=status.HTTP_201_CREATED,
        )

    except DomainError as e:
        return Response({"error": str(e)}, status=e.status_code)
    except Exception:
        logger.exception("Unexpected error in register")
        return Response(
            {"error": "Unexpected server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Handles user login requests and token generation.
    """
    try:
        username = request.data.get("username")
        password = request.data.get("password")

        tokens = login_user(username, password)

        return Response(tokens, status=status.HTTP_200_OK)

    except DomainError as e:
        return Response({"error": str(e)}, status=e.status_code)
    except Exception:
        logger.exception("Unexpected error in login")
        return Response(
            {"error": "Unexpected server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."},
                        status=status.HTTP_200_OK)

    except TokenError:
        return Response({"error": "Invalid or already blacklisted token."},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception("Unexpected error in logout")
        return Response({"error": "Unexpected server error."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
