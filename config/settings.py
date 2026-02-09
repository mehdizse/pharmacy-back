from pathlib import Path
import os

# Environment detection
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .settings_prod import *
elif ENVIRONMENT == 'development':
    from .settings_dev import *
elif ENVIRONMENT == 'staging':
    from .settings_staging import *
else:
    # Fallback to base settings
    from .settings_base import *
    
    # Basic configuration for unknown environment
    DEBUG = False
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    
    # Database fallback
    import dj_database_url
    if os.environ.get("DATABASE_URL"):
        DATABASES = {
            "default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get("DB_NAME", "pharmacy_db"),
                "USER": os.environ.get("DB_USER", "postgres"),
                "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
                "HOST": os.environ.get("DB_HOST", "localhost"),
                "PORT": os.environ.get("DB_PORT", "5432"),
            }
        }

# ======================
# DJANGO REST FRAMEWORK
# ======================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Rate limiting
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle"
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "login": "5/minute",
        "admin": "200/hour"
    },
}

# ======================
# API DOCS
# ======================
SPECTACULAR_SETTINGS = {
    "TITLE": "Pharmacy API",
    "DESCRIPTION": "API de gestion des factures et avoirs",
    "VERSION": "1.0.0",
    "TAGS": [
        {
            "name": "Authentication",
            "description": "Gestion de l'authentification et des utilisateurs"
        },
        {
            "name": "Suppliers",
            "description": "Gestion des fournisseurs"
        },
        {
            "name": "Invoices",
            "description": "Gestion des factures fournisseurs"
        },
        {
            "name": "Credit Notes",
            "description": "Gestion des avoirs fournisseurs"
        },
        {
            "name": "Reports",
            "description": "Rapports financiers et statistiques"
        },
        {
            "name": "Health",
            "description": "Vérification de santé du système"
        }
    ],
    "SCHEMA_PATH_PREFIX": "/api/",
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
}

# ======================
# CORS SETTINGS
# ======================
# Configuration dynamique des CORS depuis les variables d'environnement
cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins if origin.strip()]
CORS_ALLOW_CREDENTIALS = False  # False pour API stateless

# ======================
# DEFAULT FIELD
# ======================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
