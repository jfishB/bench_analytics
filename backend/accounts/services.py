from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


def register_user(username, email, password):
    if not username or not email or not password:
        return {"error": "All fields are required."}, status.HTTP_400_BAD_REQUEST

    if User.objects.filter(username=username).exists():
        return {"error": "Username already exists."}, status.HTTP_400_BAD_REQUEST

    if User.objects.filter(email=email).exists():
        return {"error": "Email already exists."}, status.HTTP_400_BAD_REQUEST

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    return {"message": "User created successfully!"}, status.HTTP_201_CREATED


def login_user(username, password):
    user = authenticate(username=username, password=password)

    if user is None:
        return {"error": "Invalid credentials."}, status.HTTP_401_UNAUTHORIZED

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
    }, status.HTTP_200_OK
