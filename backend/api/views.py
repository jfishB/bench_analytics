from django.http import JsonResponse
from django.db import connection

def db_health(request):
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return JsonResponse({"db": "ok"})
    except Exception as e:
        return JsonResponse({"db": "error", "detail": str(e)}, status=500)