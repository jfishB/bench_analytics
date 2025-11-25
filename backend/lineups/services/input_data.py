"""
- This file defines input data structures (dataclasses) for lineup creation.
- Imported by:
  - backend/lineups/services/lineup_creation_handler.py
  - backend/lineups/interactor.py
"""

from dataclasses import dataclass
from typing import List, Optional


# Input data structures for saving a lineup
@dataclass
class LineupPlayerInput:
    player_id: int
    batting_order: Optional[int] = None


@dataclass
class CreateLineupInput:
    team_id: int
    players: List[LineupPlayerInput]
    requested_user_id: Optional[int] = None
    name: Optional[str] = None
