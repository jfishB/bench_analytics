from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    # users endpoint
    path("register/", views.register, name="register"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("protected/", views.protected_view, name="protected"),
    path("logout/", views.logout, name="logout"),
    # JWT token routes
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
