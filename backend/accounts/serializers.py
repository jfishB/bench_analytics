"""
- This file defines the API "contract" for saving a user account
- Imported by:
  - backend/accounts/views.py
usage: CustomTokenObtainPairSerializer →
used by CustomTokenObtainPairView (login)
"""

from django.contrib.auth.models import User
from rest_framework import serializers


# Serializer for User model (currently not imported anywhere)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        