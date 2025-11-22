from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lineup, LineupPlayer
from .serializers import LineupModelSerializer, LineupOut, LineupPlayerOut
from .services.auth_user import authorize_lineup_deletion
from .services.lineup_creation_handler import (
    determine_request_mode,
    generate_suggested_lineup,
    handle_lineup_save,

)
#############################################################################
# lineups endpoint
#############################################################################
class LineupCreateView(APIView):
    """Create or generate a lineup.

    Supports two modes:
    1. Manual/Sabermetrics save: Accepts full payload with players and batting orders,
       saves to database, returns HTTP 201 with saved lineup.
    2. Algorithm-only generation: Accepts only team_id, generates suggested lineup
       without saving to database, returns HTTP 201 with suggested lineup.

    Both modes return HTTP 201 Created for API consistency.
    """

    permission_classes = [permissions.AllowAny]  # keep generation public if needed

    def post(self, request):
        # Determine request mode and get validated data if applicable
        mode, data = determine_request_mode(request.data)

        if mode == "manual_save":
            if not getattr(request.user, "is_authenticated", False):
                return Response({"detail": "Authentication required to save a lineup."}, status=status.HTTP_403_FORBIDDEN)

            # Manual or sabermetrics save - process and save to database
            lineup, lineup_players = handle_lineup_save(data, request.user) #extract lineup save 

            # Build response
            out = LineupOut(
                {
                    "id": lineup.id,
                    "team_id": lineup.team.id,
                    "name": lineup.name,
                    "players": [
                        {
                            "player_id": lp.player.id,
                            "player_name": lp.player.name,
                            "batting_order": lp.batting_order,
                        }
                        for lp in lineup_players
                    ],
                    "created_by": lineup.created_by_id,
                    "created_at": lineup.created_at,
                }
            )
            return Response(out.data, status=status.HTTP_201_CREATED)
        else:

            # Extract and validate required team_id for generation
            team_id = request.data.get("team_id")
            if team_id is None:
                return Response({"detail": "team_id is required to generate a suggested lineup"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract optional selected player ids if provided
            players_payload = request.data.get("players")
            selected_ids = None
            if isinstance(players_payload, list):
                selected_ids = [p.get("player_id") for p in players_payload if isinstance(p, dict) and p.get("player_id")]

            # Generate suggested lineup (does not save to database)
            # Note: generate_suggested_lineup expects (team_id, player_ids=None)
            suggested_players = generate_suggested_lineup(team_id, selected_ids)

            # Return suggested lineup for frontend to display
            # Use HTTP 201 Created for consistency with save endpoint
            out = {
                "team_id": team_id,
                "players": suggested_players,
            }
            return Response(out, status=status.HTTP_201_CREATED)


class LineupDeleteView(APIView):
    """Delete a saved lineup by id.

    URL:
      DELETE /api/v1/lineups/<pk>/ -> delete lineup (only creator or superuser)
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk: int):
        """Delete a lineup. Allowed only for the creator or a superuser.

        Returns 204 No Content on success, 401 if not permitted, 404 if not found.
        """
        lineup = get_object_or_404(Lineup, pk=pk)

        user = request.user

        # Authorize deletion via service authorization function
        auth_response = authorize_lineup_deletion(user, lineup)
        if auth_response is not None:
            return auth_response

        # when authorized perform delete
        lineup.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LineupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Lineup model.
    Provides CRUD operations for lineups.
    """

    serializer_class = LineupModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # debug: log auth header and request.user
        user = getattr(self.request, "user", None)

        if not user or not getattr(user, "is_authenticated", False):
            return Lineup.objects.none()
        # Super users can see everything ***CAN BE CHANGED***
        if getattr(user, "is_superuser", False):
            return Lineup.objects.all()
        return Lineup.objects.filter(created_by_id=user.id)


class LineupPlayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Player model.
    Provides CRUD operations for players.
    """

    queryset = LineupPlayer.objects.all()
    serializer_class = LineupPlayerOut
