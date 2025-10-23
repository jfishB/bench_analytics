from django.db import models


class DemoItem(models.Model):
	"""A tiny model used only for demo purposes.

	Fields:
	- name: short text
	- value: integer value
	- created_at: auto timestamp
	"""

	name = models.CharField(max_length=100)
	value = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name} ({self.value})"

