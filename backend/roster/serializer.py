from rest_framework import serializers
from .models import Team, Player


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model."""
    
    class Meta:
        model = Team
        fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model with nested team information."""
    
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = '__all__'
    
    def validate_name(self, value: str) -> str:
        """Ensure player name is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Player name cannot be empty.")
        return value.strip()


class PlayerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing players."""
    
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'team_name', 'position', 'xwoba', 'bb_percent', 'k_percent', 'barrel_batted_rate']


class PlayerRankedSerializer(PlayerSerializer):
    """Serializer for ranked players with WOS score."""
    
    wos_score = serializers.FloatField(read_only=True)
    
    class Meta(PlayerSerializer.Meta):
        fields = [
            'id', 'name', 'team', 'team_name', 'position', 'xwoba', 'bb_percent', 'k_percent', 'barrel_batted_rate', 'wos_score'
        ]
