from rest_framework import serializers

from .models import DemoItem


class DemoItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = DemoItem
		fields = ["id", "name", "value", "created_at"]
