from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
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
