from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lineup
from .models import LineupPlayer
from .serializers import LineupPlayerOut
from .serializers import LineupOut
from .serializers import LineupCreate, LineupOut, LineupCreateByTeam
from roster.models import Player as RosterPlayer
from .services.algorithm_logic import algorithm_create_lineup
from .services.auth_user import authorize_lineup_deletion
from .services.input_data import CreateLineupInput, LineupPlayerInput
from .services.validator import validate_data, validate_lineup_model
from rest_framework import viewsets


#############################################################################
# lineups endpoint
#############################################################################
class LineupCreateView(APIView):
    permission_classes = [permissions.AllowAny]  # adjust as needed

    def post(self, request):
        # Validate the body against a lightweight contract (frontend may send only team_id)
        req = LineupCreateByTeam(data=request.data)
        req.is_valid(raise_exception=True)
        data = req.validated_data

        # Load players for the requested team on the server side and build the
        # CreateLineupInput payload. This keeps the frontend thin and avoids
        # trusting client-provided player lists.
        team_id = data["team_id"]
        # TODO: clean architecture for querying players
        players_qs = list(RosterPlayer.objects.filter(team_id=team_id))
        players_input = [
            LineupPlayerInput(player_id=p.id, position=(p.position or "--")) for p in players_qs
        ]

        payload = CreateLineupInput(
            team_id=team_id,
            players=players_input,
            requested_user_id=(request.user.id if request.user.is_authenticated else None),
        )
        # TODO: decide where to validate the data 
        # Run the algorithm using the constructed payload. The algorithm will
        # validate the payload and raise domain errors if the team/players are invalid.
        # Pass the dataclass payload directly so the algorithm can run its own
        # validation lifecycle (avoid double-validating here).
        lineup, lineup_players = algorithm_create_lineup(payload)

        # Validate the produced Lineup model to ensure algorithm output is valid
        # raises exception if invalid
        validate_lineup_model(lineup)

        # Build response from the returned Lineup model. The algorithm returns
        # `lineup_players` as the persisted LineupPlayer instances, so we can
        # read `lp.player_id`, `lp.position` and `lp.batting_order` directly.
        out = LineupOut(
            {
                "id": lineup.id,
                "team_id": lineup.team_id,
                "name": lineup.name,
                "players": [
                    {
                        "player_id": lp.player_id,
                        "position": lp.position,
                        "batting_order": lp.batting_order,
                    }
                    for lp in lineup_players
                ],
                "created_by": lineup.created_by_id,
                "created_at": lineup.created_at,
            }
        )
        return Response(out.data, status=status.HTTP_201_CREATED)


# TODO: decide if we need this 
class LineupDetailView(APIView):
    """Retrieve or delete a saved lineup by id.

    URL:
      GET /api/v1/lineups/<pk>/   -> return lineup
      DELETE /api/v1/lineups/<pk>/ -> delete lineup (only creator or superuser)
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, pk: int):
        lineup = get_object_or_404(Lineup, pk=pk)

        out = LineupOut(
            {
                "id": lineup.id,
                "team_id": lineup.team_id,
                "players": [
                    {
                        "player_id": lp.player_id,
                        "position": lp.position,
                        "batting_order": lp.batting_order,
                    }
                    for lp in lineup.players.order_by("batting_order")
                ],
                "created_by": lineup.created_by_id,
                "created_at": lineup.created_at,
            }
        )

        return Response(out.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        """Delete a lineup. Allowed only for the creator or a superuser.

        Returns 204 No Content on success, 403 if not permitted, 404 if not found.
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
    ViewSet for Team model.
    Provides CRUD operations for teams.
    """

    queryset = Lineup.objects.all()
    serializer_class = LineupOut


class LineupPlayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Player model.
    Provides CRUD operations for players.
    """

    queryset = LineupPlayer.objects.all()
    serializer_class = LineupPlayerOut
