
# backend/api/views.py
from django.http import JsonResponse

def get_item(request, number):
    items = {
        1: "Rashu",
        2: "Lea",
        3: "Jeevesh",
        4: "Luke",
        5: "Ilya"
    }
    # default if number not found
    result = items.get(number, "Unknown number")
    return JsonResponse({"result": result})