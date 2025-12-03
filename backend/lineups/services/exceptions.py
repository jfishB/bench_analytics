"""
- This file defines domain-level exceptions for the lineups module.
- Imported by:
  - backend/lineups/services/validator.py
  - backend/lineups/views.py
"""


class DomainError(Exception):
    """Base class for all lineup domain exceptions."""

    def __init__(self, detail: str = "Domain error occurred."):
        super().__init__(detail)
        self.detail = detail


class TeamNotFound(DomainError):
    def __init__(self, detail: str = "Unknown team."):
        super().__init__(detail)


class PlayersNotFound(DomainError):
    def __init__(self, detail: str = "Players not found."):
        super().__init__(detail)


class PlayersWrongTeam(DomainError):
    def __init__(self, detail: str = "Players must belong to the same team."):
        super().__init__(detail)


class BadBattingOrder(DomainError):
    def __init__(self, detail: str = "Batting orders must be unique and\
                  between 1 and n."):
        super().__init__(detail)


class NoCreator(DomainError):
    def __init__(self, detail: str = "No creator found"):
        super().__init__(detail)
