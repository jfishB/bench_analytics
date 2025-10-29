from django.contrib import admin
from django.urls import path, include

# API v1 root: all public endpoints are namespaced under /api/v1/
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/lineups/", include("lineups.urls")),
    path("api/v1/auth/", include("auth.urls")),
    path("api/v1/roster/", include("roster.urls")),
]