"""
- This file defines the API views for lineup creation, retrieval, and management.
- Imported by:
  - backend/lineups/urls.py
"""

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lineup, LineupPlayer
from .serializers import LineupModelSerializer, LineupOut, LineupPlayerOut, LineupCreate
from .services.input_data import CreateLineupInput, LineupPlayerInput
from .services.validator import validate_batting_orders, validate_data
from .services.auth_user import authorize_lineup_deletion
from .services.exceptions import DomainError
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

    permission_classes = [permissions.AllowAny]  # TODO: decide 

    def post(self, request):
        """Handle POST to create or generate a lineup."""
       
        # validate request data
        serializer = LineupCreate(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Determine request mode based on already validated data
        mode, mode_data = determine_request_mode(data)

        if mode == "manual_save":
            if not getattr(request.user, "is_authenticated", False):
                return Response({"detail": "Authentication required to save a lineup."}, status=status.HTTP_403_FORBIDDEN)
            
            try:
                # Manual save: build domain payload and validate in the view
                user = request.user
                team_id = data["team_id"]
                players_data = data.get("players", [])

                players_input = [
                    LineupPlayerInput(
                        player_id=p["player_id"],
                        batting_order=p.get("batting_order"),
                    )
                    for p in players_data
                ]

                payload = CreateLineupInput(
                    team_id=team_id,
                    players=players_input,
                    requested_user_id=(user.id if user.is_authenticated else None),
                )

                # Domain validation in view layer (batting orders, team & players)
                validate_batting_orders(payload.players)
                validated = validate_data(payload)
            except DomainError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Add original players for batting_order mapping and name for service
            validated["original_players"] = payload.players
            validated["name"] = data.get("name")

            # Manual save - service only handles persistence
            lineup, lineup_players = handle_lineup_save(validated, user)

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
            # Algorithm generation path (team_id only or incomplete players)
            try:
                # Use original validated data since mode_data might be None
                team_id = data.get("team_id")
                if team_id is None:
                    return Response({"detail": "team_id is required to generate a suggested lineup"}, status=status.HTTP_400_BAD_REQUEST)

                # Extract optional selected player ids if provided
                players_payload = data.get("players")
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
            except DomainError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LineupDeleteView(APIView):
    """Delete a saved lineup by id.

    URL:
      DELETE /api/v1/lineups/<pk>/ -> delete lineup (only creator or superuser)
    """

    permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk: int):
        """Delete a lineup. Allowed only for the creator or a superuser.

        Returns 204 No Content on success, 401 if not authenticated, 403 if not permitted, 404 if not found.
        Returns 204 No Content on success, 401 if not authenticated, 403 if not permitted, 404 if not found.
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
    Provides read-only access to saved lineups.
    Create and delete operations are handled by dedicated views.
    """

    serializer_class = LineupModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        user = getattr(self.request, "user", None)

        if not user or not getattr(user, "is_authenticated", False):
            return Lineup.objects.none()
        # Super users can see everything ***CAN BE CHANGED***
        if getattr(user, "is_superuser", False):
            return Lineup.objects.all()
        return Lineup.objects.filter(created_by_id=user.id)
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
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