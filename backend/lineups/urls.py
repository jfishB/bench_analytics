
"""
- This file defines the HTTP routes (URL configuration) for the lineups module.
- Part of the web/API adapter layer; maps URLs to views only.
- Imported by: backend/config/urls.py
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import LineupCreateView, LineupDeleteView

app_name = "lineups"


router = DefaultRouter()

router.register(r"saved", views.LineupViewSet, basename="lineup")
router.register(r"lineup-players", views.LineupPlayerViewSet, basename="lineupplayer")

urlpatterns = [
    # POST /api/v1/lineups/ -> create a lineup via algorithm
    path("", LineupCreateView.as_view(), name="lineup-create"),
    # DELETE /api/v1/lineups/<id>/ -> delete a saved lineup
    path("<int:pk>/", LineupDeleteView.as_view(), name="lineup-delete"),
    # Include router-managed viewset routes (saved lineups, lineup players)
    path("", include(router.urls)),
]
