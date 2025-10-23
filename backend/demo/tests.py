from django.test import TestCase
from django.urls import reverse

from .models import DemoItem


class DemoTests(TestCase):
	def test_create_and_list(self):
		# create via service and ensure list view returns it
		item = DemoItem.objects.create(name="alpha", value=10)
		resp = self.client.get(reverse("demo-list"))
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertTrue(any(d["name"] == "alpha" for d in data))

	def test_create_endpoint(self):
		resp = self.client.post(reverse("demo-create"), {"name": "beta", "value": 5}, content_type="application/json")
		self.assertEqual(resp.status_code, 201)
		data = resp.json()
		self.assertEqual(data["name"], "beta")

	def test_increment(self):
		item = DemoItem.objects.create(name="inc", value=1)
		url = reverse("demo-increment", args=[item.id])
		resp = self.client.post(url, {"by": 4}, content_type="application/json")
		self.assertEqual(resp.status_code, 200)
		item.refresh_from_db()
		self.assertEqual(item.value, 5)

