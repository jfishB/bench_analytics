from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def get_message(request):
    with open("data.txt", "r") as f:
        message = f.read().strip()
    return Response({"message": message})

