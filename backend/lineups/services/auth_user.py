##########################################
"""
-This file defines Service functions for 
authenticating and authorizing users
- used in views
"""
###########################################
from rest_framework.response import Response

def authorize_lineup_deletion(user, lineup, Response, status) -> Response | None:
    """Authorize a user to delete a lineup.

    parameters:
        user: The user attempting the deletion.
        lineup: The lineup to be deleted.
        Response: DRF Response class for returning HTTP responses.
        status: DRF status module for HTTP status codes.

    Returns:
        A DRF Response indicating success or failure of authorization.
    """
    if not user or not user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=status.HTTP_403_FORBIDDEN)

    if lineup.created_by_id != getattr(user, "id", None) and not getattr(user, "is_superuser", False):
        return Response({"detail": "You do not have permission to delete this lineup."}, status=status.HTTP_403_FORBIDDEN)

    return None