from typing import List

from .models import DemoItem


def create_demo_item(name: str, value: int = 0) -> DemoItem:
	"""Create and return a DemoItem."""
	item = DemoItem.objects.create(name=name, value=value)
	return item


def increment_value(item_id: int, by: int = 1) -> DemoItem:
	"""Increment the value of an existing DemoItem and return it.

	Raises DemoItem.DoesNotExist if the id is invalid.
	"""
	item = DemoItem.objects.get(pk=item_id)
	item.value += by
	item.save(update_fields=["value"])
	return item


def list_items(limit: int = 50) -> List[DemoItem]:
	"""Return a list of DemoItem ordered by newest first."""
	return list(DemoItem.objects.all().order_by("-created_at")[:limit])
