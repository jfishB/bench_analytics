from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import DemoItemSerializer
from . import services


@api_view(["GET"])
def demo_list(request):
	"""Return a list of demo items."""
	items = services.list_items()
	serializer = DemoItemSerializer(items, many=True)
	return Response(serializer.data)


@api_view(["POST"])
def demo_create(request):
	"""Create a demo item. Expects JSON: {"name": str, "value": int} """
	name = request.data.get("name")
	value = request.data.get("value", 0)
	if not name:
		return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)
	item = services.create_demo_item(name=name, value=int(value))
	return Response(DemoItemSerializer(item).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def demo_increment(request, item_id: int):
	"""Increment a demo item's value. Expects JSON: {"by": int} """
	by = int(request.data.get("by", 1))
	try:
		item = services.increment_value(item_id, by=by)
	except Exception as exc:
		return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
	return Response(DemoItemSerializer(item).data)

