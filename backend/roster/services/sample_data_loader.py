"""
Service for loading sample player data from CSV.
Handles finding the CSV file and importing players to the database.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from roster.models import Player, Team
from roster.services.importer import import_from_csv


def get_csv_path() -> Optional[str]:
    """
    Find the sample CSV file in possible locations.
    Returns the path if found, None otherwise.
    """
    csv_candidates = [
        # From repo root (Render deployment)
        Path("data/test_dataset_monte_carlo_bluejays.csv"),
        # From backend/ dir (local development)
        Path("../data/test_dataset_monte_carlo_bluejays.csv"),
    ]

    for candidate in csv_candidates:
        if candidate.exists():
            return str(candidate)

    return None


def load_sample_players(team_id: int = 1) -> Dict[str, Any]:
    """
    Load sample players from CSV into the database.

    Args:
        team_id: Team ID to assign players to (default: 1)

    Returns:
        Dict with status information including:
        - success: bool
        - already_loaded: bool
        - players_count: int
        - team_id: int
        - loaded/updated counts
        - error message if failed
    """
    # Ensure the default team exists
    default_team, _ = Team.objects.get_or_create(pk=team_id)

    # Check if players already exist
    players_count = Player.objects.count()
    if players_count > 0:
        # Assign any players without a team to the default team
        players_without_team = Player.objects.filter(team__isnull=True)
        updated_count = players_without_team.update(team=default_team)

        return {
            "success": True,
            "already_loaded": True,
            "players_count": players_count,
            "team_id": default_team.id,
            "players_assigned_to_team": updated_count,
            "message": (
                f"Players already loaded. Assigned {updated_count} to team."
                if updated_count > 0
                else "Players are already loaded."
            ),
        }

    # Find the CSV file
    csv_path = get_csv_path()
    if not csv_path:
        return {
            "success": False,
            "error": "CSV file not found",
        }

    # Import players
    result = import_from_csv(csv_path, team_id=default_team.id)

    return {
        "success": True,
        "already_loaded": False,
        "players_count": Player.objects.count(),
        "team_id": default_team.id,
        "loaded": result.get("created", 0),
        "updated": result.get("updated", 0),
        "messages": result.get("messages", []),
    }
