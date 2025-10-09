from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Player

# Create your views here.


def hello(request):
    return JsonResponse({"message": "Hello from Django!"})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def players(request):
    if request.method == "GET":
        # Get all players from database
        players_list = list(Player.objects.values("id", "name", "team", "created_at"))
        return JsonResponse(players_list, safe=False)

    elif request.method == "POST":
        # Add new player to database
        try:
            data = json.loads(request.body)
            player = Player.objects.create(
                name=data.get("name"),
                team=data.get("team"),
            )
            return JsonResponse(
                {
                    "message": "Player added successfully!",
                    "player": {
                        "id": player.id,
                        "name": player.name,
                        "team": player.team,
                        "created_at": player.created_at.isoformat(),
                    },
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_player(request, player_id):
    try:
        player = Player.objects.get(id=player_id)
        player.delete()
        return JsonResponse({"message": f"Player {player_id} deleted successfully!"})
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
