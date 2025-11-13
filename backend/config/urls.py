from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

# API v1 root: all public endpoints are namespaced under /api/v1/
urlpatterns = [
    # Redirect the root URL to the saved lineups list so visiting
    # http://127.0.0.1:8000/ shows a useful page instead of a 404.
    path("", RedirectView.as_view(url="/api/v1/lineups/saved/", permanent=False)),

    path("admin/", admin.site.urls),
    # Backwards-compatible alias (no /v1/) for older clients that call /api/players/
    path("api/players/", include("roster.urls")),
    path("api/lineup/", include("lineups.urls")),
    path("api/v1/lineups/", include("lineups.urls")),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/roster/", include("roster.urls")),
]
