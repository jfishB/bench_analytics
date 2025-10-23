from django.contrib import admin

from .models import DemoItem


@admin.register(DemoItem)
class DemoItemAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "value", "created_at")
	readonly_fields = ("created_at",)

