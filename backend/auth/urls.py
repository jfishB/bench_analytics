from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

app_name = "auth"

urlpatterns = [
    # users endpoint
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('protected/', views.protected_view, name='protected'),

    # JWT token routes
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
