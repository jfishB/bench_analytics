from django.test import TestCase
from rest_framework.exceptions import ValidationError

from roster.models import Player, Team
from roster.serializer import (
    PlayerCreateSerializer,
    PlayerPartialUpdateSerializer,
    PlayerSerializer,
)


class PlayerSerializerTestCase(TestCase):
    """Test PlayerSerializer validation."""

    def setUp(self):
        self.team = Team.objects.create(id=1)

    def test_player_create_serializer_valid_name(self):
        """Test creating a player with valid name."""
        data = {
            "name": "Test Player",
            "team": self.team.id,
            "pa": 100,
        }
        serializer = PlayerCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_player_create_serializer_empty_name(self):
        """Test that empty player name raises validation error."""
        data = {
            "name": "   ",  # Only whitespace
            "team": self.team.id,
            "pa": 100,
        }
        serializer = PlayerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_player_partial_update_serializer_empty_name(self):
        """Test that empty name in partial update raises validation error."""
        player = Player.objects.create(name="Original Name", team=self.team, pa=100)
        
        data = {"name": "   "}  # Only whitespace
        serializer = PlayerPartialUpdateSerializer(player, data=data, partial=True)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_player_partial_update_serializer_none_name(self):
        """Test that None name in partial update is handled correctly."""
        player = Player.objects.create(name="Original Name", team=self.team, pa=100)
        
        # Partial update without name field should work
        data = {"pa": 200}
        serializer = PlayerPartialUpdateSerializer(player, data=data, partial=True)
        
        self.assertTrue(serializer.is_valid())

    def test_mixin_validate_name_direct(self):
        """Test PlayerNameValidationMixin.validate_name directly."""
        from roster.serializer import PlayerNameValidationMixin
        mixin = PlayerNameValidationMixin()
        
        # Test valid name
        self.assertEqual(mixin.validate_name(" Valid Name "), "Valid Name")
        
        # Test empty name raises ValidationError
        with self.assertRaises(ValidationError):
            mixin.validate_name("   ")

    def test_partial_update_validate_name_direct(self):
        """Test PlayerPartialUpdateSerializer.validate_name directly."""
        serializer = PlayerPartialUpdateSerializer()
        
        # Test valid name
        self.assertEqual(serializer.validate_name(" Valid Name "), "Valid Name")
        
        # Test empty name raises ValidationError
        with self.assertRaises(ValidationError):
            serializer.validate_name("   ")
        
        # Test None/empty value returns as is (if logic allows, though validate_name usually gets value)
        # The code says: if value and not value.strip(): raise
        # So if value is None, it returns None
        self.assertIsNone(serializer.validate_name(None))
        self.assertEqual(serializer.validate_name(""), "")
