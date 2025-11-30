"""
- This file defines the API "contract" for saving a user account
- Imported by:
  - backend/accounts/views.py
usage: CustomTokenObtainPairSerializer →
used by CustomTokenObtainPairView (login)
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Serializer for User model (currently not imported anywhere)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT to include user information in the login response.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user data to the response
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["id"] = self.user.id
        return data
