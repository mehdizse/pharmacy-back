"""
URL configuration for pharmacy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def api_info(request):
    """API root endpoint with basic information"""
    return JsonResponse({
        'message': 'Pharmacy Backend API',
        'version': '1.0.0',
        'docs': '/api/docs/',
        'schema': '/api/schema/',
        'health': '/api/health/',
        'endpoints': {
            'auth': '/api/auth/',
            'suppliers': '/api/suppliers/',
            'invoices': '/api/invoices/',
            'credit_notes': '/api/credit-notes/',
            'reports': '/api/reports/'
        }
    })

urlpatterns = [
    # Root endpoint
    path('', api_info, name='api-info'),
    
    path('admin/', admin.site.urls),
    
    # API Documentation - DÉSACTIVÉ EN PRODUCTION
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/health/', include('apps.health.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/suppliers/', include('apps.suppliers.urls')),
    path('api/invoices/', include('apps.invoices.urls')),
    path('api/credit-notes/', include('apps.credit_notes.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

# Static files for production (WhiteNoise)
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Handler pour les pages d'erreur personnalisées
handler404 = 'config.views.custom_404'
handler500 = 'config.views.custom_500'
handler403 = 'config.views.custom_403'

# Import pour éviter les erreurs circulaires
from django.conf import settings
