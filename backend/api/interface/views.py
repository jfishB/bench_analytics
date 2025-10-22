from django.http import JsonResponse
from django.db import connection
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from api.contracts.lineups_contract import LineupCreate, LineupOut
from .models import Team, Player, Lineup, LineupPlayer
from .models import Player


def db_health(request):
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return JsonResponse({"db": "ok"})
    except Exception as e:
        return JsonResponse({"db": "error", "detail": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def players(request):
    """API endpoint to list and create players."""
    if request.method == "GET":
        # List all players
        players = Player.objects.all()
        player_data = [
            {
                "id": player.id,
                "name": player.name,
                "created_at": player.created_at.isoformat(),
                "updated_at": player.updated_at.isoformat(),
            }
            for player in players
        ]
        return JsonResponse({"players": player_data})

    elif request.method == "POST":
        # Create a new player
        try:
            data = json.loads(request.body)
            name = data.get("name")

            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)

            player = Player.objects.create(name=name)
            return JsonResponse(
                {
                    "id": player.id,
                    "name": player.name,
                    "created_at": player.created_at.isoformat(),
                    "updated_at": player.updated_at.isoformat(),
                },
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def player_detail(request, player_id):
    """API endpoint to delete a specific player."""
    try:
        player = Player.objects.get(id=player_id)
        player_name = player.name
        player.delete()
        return JsonResponse({"message": f"Player '{player_name}' deleted successfully"})
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    

#############################################################################
# lineups endpoint using DRF and contracts
#############################################################################   
class LineupCreateView(APIView):
    permission_classes = [permissions.AllowAny] # adjust as needed

    def post(self, request):
        # Validate the body against the request contract
        req = LineupCreate(data=request.data) # takes client data and sends to the serializer
        req.is_valid(raise_exception=True) # checks that the input data is valid
        data = req.validated_data  # the validated data from the request which is now safe to use


        team = Team.objects.filter(pk=data["team_id"]).first()   # get the team object or None
        if not team:
            return Response({"team_id": ["Unknown team."]}, status=404) # if team_id is invalid, return error

        ids = [p["player_id"] for p in data["players"]]
        players = list(Player.objects.filter(id__in=ids).select_related("team"))  # get all players in one query with their teams
        if len(players) != len(ids):
            return Response({"players": ["Players not found"]}, status=400)
        if any(p.team_id != team.id for p in players):
            return Response({"players": ["Players must belong to the same team."]}, status=400)
        
        orders = [p["batting_order"] for p in data["players"]]
        if sorted(orders) != list(range(1, len(orders)+1)):  # check if orders are unique and between 1 and 9       
            return Response({"players": ["Batting orders must be unique and between 1 and 9."]}, status=400)        
        
        # Validate opponent pitcher (FETCH BEFORE USING)
        opp_pitcher_id = data["opponent_pitcher_id"]
        opp_pitcher = (
            Player.objects.select_related("team").filter(pk=opp_pitcher_id).first()
        )
        if not opp_pitcher:
            return Response({"opponent_pitcher_id": ["Opponent pitcher not found."]}, status=404)

        opp_team_id = data.get("opponent_team_id")
        if opp_team_id is not None and opp_team_id != opp_pitcher.team_id:
            return Response({"opponent_team_id": ["Does not match opponent_pitcher’s team."]}, status=400)

        batter_ids = set(ids)
        if opp_pitcher.id in batter_ids:
            return Response({"players": ["Opponent pitcher cannot appear in batting lineup."]}, status=400)
        
        # Determine created_by
        User = get_user_model()
        if request.user.is_authenticated:
            created_by_id = request.user.id
        else:
            created_by_id = User.objects.filter(is_superuser=True).values_list("id", flat=True).first()
            if created_by_id is None:
                return Response(
                    {"detail": "No authenticated user and no superuser exists. Create one or authenticate."},
                    status=400,
            )
        # Create Lineup and LineupPlayers in a transaction
        with transaction.atomic():
            lineup = Lineup.objects.create(
                team=team,
                name=data["name"],
                opponent_pitcher_id=opp_pitcher.id,
                opponent_team_id=opp_team_id,
                created_by_id=created_by_id,  # <-- use *_id, not the AnonymousUser object
            )

            # Create LineupPlayer entries
            by_id = {p["player_id"]: p for p in data["players"]}
            for pl in players:
                slot = by_id[pl.id]
                LineupPlayer.objects.create(
                    lineup=lineup,
                    player=pl,
                    position=slot["position"],
                    batting_order=slot["batting_order"],
                )

        # Format response with the response contract
        out = LineupOut({
            "id": lineup.id,
            "team_id": lineup.team_id,
            "name": lineup.name,
            "opponent_pitcher_id": lineup.opponent_pitcher_id,
            "opponent_team_id": lineup.opponent_team_id,
            "players": [
                {"player_id": lp.player_id, "position": lp.position, "batting_order": lp.batting_order}
                for lp in lineup.players.order_by("batting_order")
            ],
            "created_by": request.user.id if request.user.is_authenticated else None,
            "created_at": lineup.created_at,
        })
        return Response(out.data, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello, {request.user.username}!"})
    
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username,
        })
    else:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)