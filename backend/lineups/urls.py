from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LineupCreateView, LineupDetailView
from . import views

app_name = "lineups"

# Use a router for saved lineups / related resources. We register the
# viewsets under non-conflicting prefixes because this module is already
# included at /api/v1/lineups/ at the project level.
router = DefaultRouter()
# Saved lineups (CRUD for persisted Lineup objects) will be available at
# /api/v1/lineups/saved/ and /api/v1/lineups/saved/<pk>/
router.register(r"saved", views.LineupViewSet, basename="lineup")
# LineupPlayer resources under /api/v1/lineups/lineup-players/
router.register(r"lineup-players", views.LineupPlayerViewSet, basename="lineupplayer")

# When included under the project urls as api/v1/lineups/, the explicit
# endpoints below remain available at the base path. These implement the
# algorithm-backed create endpoint and a simple detail/delete view.
urlpatterns = [
    # POST /api/v1/lineups/ -> create a lineup via algorithm
    path("", LineupCreateView.as_view(), name="lineup-create"),
    # GET/DELETE /api/v1/lineups/<id>/ -> view or delete a saved lineup
    path("<int:pk>/", LineupDetailView.as_view(), name="lineup-detail"),
    # Include router-managed viewset routes (saved lineups, lineup players)
    path("", include(router.urls)),
]
