##########################################
"""
- This file contains the custom exceptions
- used in lineup validator.
"""
###########################################


class TeamNotFound(Exception):
    def __init__(self, detail: str = "Unknown team."):
        super().__init__(detail)
        self.detail = detail


class PlayersNotFound(Exception):
    def __init__(self, detail: str = "Players not found."):
        super().__init__(detail)
        self.detail = detail


class PlayersWrongTeam(Exception):
    def __init__(self, detail: str = "Players must belong to the same team."):
        super().__init__(detail)
        self.detail = detail


class BadBattingOrder(Exception):
    def __init__(self, detail: str = "Batting orders must be unique and between 1 and n."):
        super().__init__(detail)
        self.detail = detail


class NoCreator(Exception):
    def __init__(self, detail: str = "No creator found"):
        super().__init__(detail)
        self.detail = detail
