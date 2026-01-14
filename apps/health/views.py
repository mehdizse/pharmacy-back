from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings
from django.utils import timezone
import json


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint pour monitoring et status du backend
    """
    try:
        # Vérifier la connexion à la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Statut global
    is_healthy = db_status == "healthy"
    
    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production",
        "services": {
            "database": {
                "status": db_status,
                "engine": settings.DATABASES["default"]["ENGINE"]
            },
            "api": {
                "status": "healthy",
                "version": "1.0.0"
            }
        },
        "endpoints": {
            "documentation": "/api/docs/",
            "schema": "/api/schema/",
            "auth": "/api/auth/",
            "suppliers": "/api/suppliers/",
            "invoices": "/api/invoices/",
            "credit_notes": "/api/credit-notes/",
            "reports": "/api/reports/"
        }
    }
    
    status_code = 200 if is_healthy else 503
    return JsonResponse(response_data, status=status_code)
