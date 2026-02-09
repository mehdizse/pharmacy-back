"""
Secure URLs for JWT authentication
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .secure_views import SecureInvoiceViewSet
from apps.accounts.jwt_views import (
    CustomTokenObtainPairView,
    jwt_refresh_view,
    jwt_logout_view,
)

router = DefaultRouter()
router.register(r'invoices', SecureInvoiceViewSet, basename='invoice')

app_name = 'invoices_secure'

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='jwt_login'),
    path('auth/refresh/', jwt_refresh_view, name='jwt_refresh'),
    path('auth/logout/', jwt_logout_view, name='jwt_logout'),
    
    # Invoice endpoints (sécurisés)
    path('', include(router.urls)),
]
