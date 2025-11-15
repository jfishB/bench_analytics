"""
Serializers for the simulator app.
Handles request/response validation and transformation.
"""

from rest_framework import serializers


class PlayerInputSerializer(serializers.Serializer):
    """Input serializer for specifying players by ID."""
    player_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=9,
        max_length=9,
        help_text="List of exactly 9 player IDs in batting order"
    )
    num_games = serializers.IntegerField(
        default=1000,
        min_value=100,
        max_value=100000,
        help_text="Number of games to simulate"
    )


class PlayerNameInputSerializer(serializers.Serializer):
    """Input serializer for specifying players by name."""
    player_names = serializers.ListField(
        child=serializers.CharField(),
        min_length=9,
        max_length=9,
        help_text="List of exactly 9 player names in batting order"
    )
    num_games = serializers.IntegerField(
        default=1000,
        min_value=100,
        max_value=100000,
        help_text="Number of games to simulate"
    )


class TeamInputSerializer(serializers.Serializer):
    """Input serializer for using a team's top players."""
    team_id = serializers.IntegerField(help_text="Team ID to use")
    num_games = serializers.IntegerField(
        default=1000,
        min_value=100,
        max_value=100000,
        help_text="Number of games to simulate"
    )


class BatterStatsOutputSerializer(serializers.Serializer):
    """Output serializer for individual batter stats."""
    name = serializers.CharField()
    plate_appearances = serializers.IntegerField()
    hits = serializers.IntegerField()
    doubles = serializers.IntegerField()
    triples = serializers.IntegerField()
    home_runs = serializers.IntegerField()
    strikeouts = serializers.IntegerField()
    walks = serializers.IntegerField()


class SimulationResultSerializer(serializers.Serializer):
    """Output serializer for simulation results."""
    lineup = serializers.ListField(
        child=serializers.CharField(),
        help_text="Player names in batting order"
    )
    num_games = serializers.IntegerField()
    avg_score = serializers.FloatField()
    median_score = serializers.FloatField()
    std_dev = serializers.FloatField()
    min_score = serializers.IntegerField()
    max_score = serializers.IntegerField()
    score_distribution = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Mapping of score -> frequency"
    )
