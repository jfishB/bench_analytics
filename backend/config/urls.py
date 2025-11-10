from django.contrib import admin
from django.urls import include, path

# API v1 root: all public endpoints are namespaced under /api/v1/
urlpatterns = [
    path("admin/", admin.site.urls),
    # Backwards-compatible alias (no /v1/) for older clients that call /api/players/
    path("api/players/", include("roster.urls")),
    path("api/v1/lineups/", include("lineups.urls")),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/roster/", include("roster.urls")),
    path('api/accounts/', include('accounts.urls')),
]
