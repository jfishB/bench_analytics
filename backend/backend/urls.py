"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from api import views
from api.views import LineupCreateView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/db/", views.db_health),  # <-- health endpoint
    path("api/players/", views.players),  # <-- players endpoint
    path(
        "api/players/<int:player_id>/", views.player_detail
    ),  # <-- individual player endpoint
    path("api/v1/lineups/", LineupCreateView.as_view(), name="lineup-create"),  # <-- lineup saving endpoint
    path('api/', include('api.urls')),
]
