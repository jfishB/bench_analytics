from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lineups/", include("lineups.urls")),
    path("auth/", include("auth.urls")),
]