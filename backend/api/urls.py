from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('protected/', views.protected_view, name='protected'),

    # JWT token routes
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Player endpoints
    path('players/', views.players, name='players'),
    path('players/<int:player_id>/', views.player_detail, name='player_detail'),
    path('players/ranked/', views.players_ranked, name='players_ranked'),
]
