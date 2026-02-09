"""
Secure URLs for multi-tenant architecture
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .multi_tenant_views import MultiTenantInvoiceViewSet
from apps.accounts.jwt_views import (
    CustomTokenObtainPairView,
    jwt_refresh_view,
    jwt_logout_view
)

router = DefaultRouter()
router.register(r'invoices', MultiTenantInvoiceViewSet, basename='invoice')

app_name = 'invoices_multi_tenant'

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='jwt_login'),
    path('auth/refresh/', jwt_refresh_view, name='jwt_refresh'),
    path('auth/logout/', jwt_logout_view, name='jwt_logout'),
    
    # Invoice endpoints (sécurisés)
    path('', include(router.urls)),
]
