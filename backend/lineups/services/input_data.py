##########################################
"""
- This file contains the input data structures
- used in views
"""
###########################################
from dataclasses import dataclass
from typing import List, Optional


# Input data structures for saving a lineup
@dataclass
class LineupPlayerInput:
    player_id: int
    position: str
    batting_order: Optional[int] = None


@dataclass
class CreateLineupInput:
    team_id: int
    name: str
    players: List[LineupPlayerInput]
    requested_user_id: Optional[int] = None
