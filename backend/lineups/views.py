from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lineup
from .serializers import LineupCreate, LineupOut
from .services.algorithm_logic import algorithm_create_lineup
from .services.auth_user import authorize_lineup_deletion
from .services.input_data import CreateLineupInput, LineupPlayerInput
from .services.validator import validate_lineup_model


#############################################################################
# lineups endpoint
#############################################################################
class LineupCreateView(APIView):
    permission_classes = [permissions.AllowAny]  # adjust as needed

    def post(self, request):
        # Validate the body against the request contract
        req = LineupCreate(
            data=request.data
        )  # takes client data and sends to the serializer
        req.is_valid(
            raise_exception=True
        )  # checks that the input data is valid; this is built into Django REST Framework
        data = (
            req.validated_data
        )  # the validated data from the request which is now safe to use

        payload = CreateLineupInput(
            team_id=data["team_id"],
            name=data["name"],
            players=[
                LineupPlayerInput(
                    player_id=p["player_id"],
                    position=p["position"],
                )
                for p in data["players"]
            ],
            requested_user_id=(
                request.user.id if request.user.is_authenticated else None
            ),
        )

        # Run the algorithm to create the lineup.
        lineup = algorithm_create_lineup(payload)

        # Validate the produced Lineup model to ensure algorithm output is valid
        # raises exception if invalid
        validate_lineup_model(lineup)

        # Build response from the returned Lineup model.
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
                    for lp in lineup.players.order_by("batting_order")
                ],
                "created_by": lineup.created_by_id,
                "created_at": lineup.created_at,
            }
        )
        return Response(out.data, status=status.HTTP_201_CREATED)


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
