"""
Production settings for Pharmacy Backend
NEVER use this file directly - import via environment
"""
from .settings_base import *
import os

# ======================
# SECURITY - PRODUCTION ONLY
# ======================
DEBUG = False

# Validate SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or SECRET_KEY == 'django-insecure-dev-key':
    raise ValueError("SECRET_KEY must be set and cannot be the default value!")

# ======================
# SECURE SETTINGS
# ======================
# Permettre de désactiver SSL redirect pour le staging/testing
DISABLE_SSL_REDIRECT = os.environ.get('DISABLE_SSL_REDIRECT', 'false').lower() == 'true'
SECURE_SSL_REDIRECT = not DISABLE_SSL_REDIRECT
SESSION_COOKIE_SECURE = not DISABLE_SSL_REDIRECT
CSRF_COOKIE_SECURE = not DISABLE_SSL_REDIRECT

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ======================
# MIDDLEWARE - PRODUCTION
# ======================
# API STATELESS = PAS de CSRF middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",  # OBLIGATOIRE
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # SÉCURITÉ: PAS de django.middleware.csrf.CsrfViewMiddleware pour API stateless
]

# ======================
# CORS - PRODUCTION
# ======================
def get_cors_origins():
    """Get and validate CORS origins"""
    origins_str = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://localhost:3000,https://localhost:4200')
    
    # Éviter les chaînes vides
    if not origins_str or not origins_str.strip():
        return ['https://localhost:3000', 'https://localhost:4200']
    
    origins = origins_str.split(',')
    validated_origins = [origin.strip() for origin in origins if origin.strip()]
    
    # Filtrer les chaînes vides et valider le format
    validated_origins = [origin for origin in validated_origins if origin and ('://' in origin)]
    
    if not validated_origins:
        raise ValueError("CORS_ALLOWED_ORIGINS must be set in production")
    
    return validated_origins

CORS_ALLOWED_ORIGINS = get_cors_origins()
CORS_ALLOW_ALL_ORIGINS = False  # TOUJOURS False en production
CORS_ALLOW_CREDENTIALS = False  # False pour API stateless

# ======================
# DATABASE - PRODUCTION
# ======================
import dj_database_url

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "pharmacy_staging"),
            "USER": os.environ.get("DB_USER", "staging_user"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# ======================
# ALLOWED HOSTS
# ======================
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ======================
# JWT CONFIGURATION
# ======================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ======================
# DJANGO REST FRAMEWORK
# ======================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.jwt_auth.CustomJWTAuthentication",
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
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle"
    ],
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/minute",
        "refresh": "10/minute", 
        "admin": "200/hour",
        "anon": "100/hour",
        "user": "1000/hour",
        "sensitive": "10/hour",
    },
    "DEFAULT_THROTTLE_SCOPE": "user",
}

# ======================
# LOGGING - PRODUCTION
# ======================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
        'secure': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'sensitive_data': {
            '()': 'apps.logging.filters.SensitiveDataFilter',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',  # Utiliser StreamHandler pour compatibilité
            'formatter': 'json',
            'filters': ['sensitive_data'],
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'secure',
            'filters': ['sensitive_data'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.reports': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
}
