from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@api_view(["POST"])
def echo_input(request):
    user_input = request.data.get("text", "")
    return Response({"processed": f"You said: {user_input}"})