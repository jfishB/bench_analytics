from django.urls import path

from .views import LineupCreateView

app_name = "lineups"

# When included under the project urls as api/v1/lineups/, the
# endpoint below will be available at /api/v1/lineups/ (POST to create).
urlpatterns = [
    # POST /api/v1/lineups/ -> create a lineup
    path("", LineupCreateView.as_view(), name="lineup-create"),
]
