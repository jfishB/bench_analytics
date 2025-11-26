"""
- This file defines the API views for lineup creation, retrieval, and management.
- Imported by:
  - backend/lineups/urls.py
"""

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .interactor import LineupCreationInteractor
from .models import Lineup, LineupPlayer
from .serializers import LineupModelSerializer, LineupOut, LineupPlayerOut, LineupCreate
from .services.auth_user import authorize_lineup_deletion
from .services.exceptions import DomainError
from .services.lineup_creation_handler import (
    determine_request_mode,
)
#############################################################################
# lineups endpoint
#############################################################################
class LineupCreateView(APIView):
    """Create or generate a lineup.
    URL:
      POST /api/v1/lineups/ -> create or generate lineup
    Delegates to interactor for use case handling.
    """
    permission_classes = [permissions.AllowAny]  # TODO: decide 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interactor = LineupCreationInteractor()
    
    def post(self, request):
        # 1. Deserialize HTTP request
        serializer = LineupCreate(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # 2. Determine mode
        mode, _ = determine_request_mode(data)
        
        # 3. Call appropriate interactor method
        try:
            if mode == "manual_save":
                # Check authentication for save operations
                if not getattr(request.user, "is_authenticated", False):
                    return Response(
                        {"detail": "Authentication required to save a lineup."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                lineup, lineup_players = self.interactor.create_manual_lineup(
                    team_id=data["team_id"],
                    players_data=data.get("players"),
                    user_id=request.user.id,
                    name=data.get("name")
                )
                return self._build_saved_response(lineup, lineup_players)
            else:
                # Extract optional player IDs for algorithm
                selected_ids = self._extract_player_ids(data)
                
                suggested_players = self.interactor.generate_suggested_lineup(
                    team_id=data.get("team_id"),
                    selected_player_ids=selected_ids
                )
                return self._build_suggested_response(data.get("team_id"), suggested_players)
        except DomainError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Helper methods 
    def _build_saved_response(self, lineup, lineup_players):
        """Transform domain objects (lineup, lineup_players) to HTTP Response."""
        out = LineupOut({
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
        })
        return Response(out.data, status=status.HTTP_201_CREATED)
    
    def _build_suggested_response(self, team_id, suggested_players):
        """Transform suggested players to HTTP Response."""
        out = {
            "team_id": team_id,
            "players": suggested_players,
        }
        return Response(out, status=status.HTTP_201_CREATED)
    
    def _extract_player_ids(self, data):
        """Extract optional player IDs from validated data."""
        players_payload = data.get("players")
        if isinstance(players_payload, list):
            return [
                p.get("player_id") 
                for p in players_payload 
                if isinstance(p, dict) and p.get("player_id")
            ]
        return None


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