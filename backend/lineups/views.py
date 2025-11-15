from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from roster.models import Player as RosterPlayer

from .models import Lineup, LineupPlayer
from .serializers import (
    LineupCreate,
    LineupCreateByTeam,
    LineupModelSerializer,
    LineupOut,
    LineupPlayerOut,
)
from .services.algorithm_logic import algorithm_create_lineup
from .services.auth_user import authorize_lineup_deletion
from .services.input_data import CreateLineupInput, LineupPlayerInput
from .services.validator import validate_data, validate_lineup_model


#############################################################################
# lineups endpoint
#############################################################################
class LineupCreateView(APIView):
    permission_classes = [permissions.AllowAny]  # adjust as needed

    def post(self, request):
        # Try to validate with full payload first (manual/sabermetrics save with players and batting orders)
        req_full = LineupCreate(data=request.data)

        if req_full.is_valid():
            # Full payload provided - check if batting orders are set
            data = req_full.validated_data
            players_data = data["players"]
            all_have_batting_order = all(
                p.get("batting_order") is not None for p in players_data
            )

            if all_have_batting_order:
                # Manual or sabermetrics save - skip algorithm and save directly
                team_id = data["team_id"]
                lineup_name = (
                    data.get("name")
                    or f"Lineup - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                )

                # Build CreateLineupInput with provided batting orders
                players_input = [
                    LineupPlayerInput(
                        player_id=p["player_id"],
                        position=p["position"],
                        batting_order=p.get("batting_order"),
                    )
                    for p in players_data
                ]

                payload = CreateLineupInput(
                    team_id=team_id,
                    players=players_input,
                    requested_user_id=(
                        request.user.id if request.user.is_authenticated else None
                    ),
                )

                # Validate data
                validated = validate_data(payload)
                team_obj = validated["team"]
                players_list = validated["players"]
                created_by_id = validated["created_by_id"]

                # Build batting order and position mappings from payload
                batting_orders = {}
                position_map = {}
                for p in payload.players:
                    batting_orders[p.player_id] = p.batting_order
                    position_map[p.player_id] = p.position

                # Save lineup directly in transaction
                with transaction.atomic():
                    User = get_user_model()
                    created_by = User.objects.get(pk=created_by_id)

                    lineup = Lineup.objects.create(
                        team=team_obj,
                        name=lineup_name,
                        created_by=created_by,
                    )

                    # Create LineupPlayer entries with provided batting orders
                    lineup_players = []
                    for player in players_list:
                        position = position_map.get(player.id, player.position)
                        batting_order = batting_orders.get(player.id)

                        lineup_player = LineupPlayer.objects.create(
                            lineup=lineup,
                            player=player,
                            position=position,
                            batting_order=batting_order,
                        )
                        lineup_players.append(lineup_player)

                # Validate the produced Lineup model
                validate_lineup_model(lineup)

                # Build response
                out = LineupOut(
                    {
                        "id": lineup.id,
                        "team_id": lineup.team_id,
                        "name": lineup.name,
                        "players": [
                            {
                                "player_id": lp.player_id,
                                "player_name": lp.player.name,
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

        # Fall back to algorithm mode (team_id only)
        # This is now only for "Generate Lineup" button - should NOT save to DB
        # It just runs the algorithm and returns the suggested lineup
        req = LineupCreateByTeam(data=request.data)
        req.is_valid(raise_exception=True)
        data = req.validated_data

        team_id = data["team_id"]

        # Load all players for the team
        players_qs = list(RosterPlayer.objects.filter(team_id=team_id))

        # Run algorithm logic inline to get batting order WITHOUT saving
        from .services.algorithm_logic import calculate_spot_scores

        # Greedy assignment algorithm (same as in algorithm_logic.py but without saving)
        available_indices = set(range(len(players_qs)))
        assignments = {}  # batting_order -> player_index

        for spot in range(1, 10):  # Spots 1 through 9
            scores = calculate_spot_scores(players_qs, spot)
            best_idx = None
            best_score = -float("inf") if spot != 9 else float("inf")

            for idx in available_indices:
                if spot == 9:
                    if scores[idx] < best_score:
                        best_score = scores[idx]
                        best_idx = idx
                else:
                    if scores[idx] > best_score:
                        best_score = scores[idx]
                        best_idx = idx

            if best_idx is not None:
                assignments[spot] = best_idx
                available_indices.remove(best_idx)

        # Build response with suggested lineup (NO DATABASE SAVE)
        suggested_players = []
        for batting_order, player_idx in sorted(assignments.items()):
            player = players_qs[player_idx]
            suggested_players.append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "position": player.position or "DH",
                    "batting_order": batting_order,
                }
            )

        # Return the suggested lineup WITHOUT saving to database
        # Frontend will display this and user can save it later with their chosen name
        out = {
            "team_id": team_id,
            "players": suggested_players,
        }
        return Response(out, status=status.HTTP_200_OK)


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
                "name": lineup.name,
                "players": [
                    {
                        "player_id": lp.player_id,
                        "player_name": (
                            lp.player.name
                            if getattr(lp, "player", None) is not None
                            else None
                        ),
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
    ViewSet for Lineup model.
    Provides CRUD operations for lineups.
    """

    queryset = Lineup.objects.all()
    serializer_class = LineupModelSerializer


class LineupPlayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Player model.
    Provides CRUD operations for players.
    """

    queryset = LineupPlayer.objects.all()
    serializer_class = LineupPlayerOut
