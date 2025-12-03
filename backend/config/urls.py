"""  # pragma: no cover
Global URL configuration for the Django project.  # pragma: no cover
"""  # pragma: no cover
from django.contrib import admin  # pragma: no cover
from django.urls import include, path  # pragma: no cover
from django.views.generic import RedirectView  # pragma: no cover

urlpatterns = [  # pragma: no cover
    # Redirect the root URL to the saved lineups list so visiting  # pragma: no cover
    # http://127.0.0.1:8000/ shows a useful page instead of a 404.  # pragma: no cover
    path("", RedirectView.as_view(url="/api/v1/lineups/saved/",  # pragma: no cover
                                  permanent=False)),  # pragma: no cover
    path("admin/", admin.site.urls),  # pragma: no cover
    path("api/v1/lineups/", include("lineups.urls")),  # pragma: no cover
    path("api/v1/auth/", include("accounts.urls")),  # pragma: no cover
    path("api/v1/roster/", include("roster.urls")),  # pragma: no cover
    path("api/v1/simulator/", include("simulator.urls")),  # pragma: no cover
]  # pragma: no cover
