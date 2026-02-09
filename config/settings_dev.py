"""
Development settings for Pharmacy Backend
"""
from .settings_base import *

# ======================
# DEVELOPMENT OVERRIDES
# ======================
DEBUG = True

# ======================
# ALLOWED HOSTS - DEV
# ======================
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost", 
    "0.0.0.0",
]

# Port du backend pour éviter les conflits avec Angular
# Utilise :8000 (standard) et Angular sur :4201
RUNSERVER_PORT = 8000

# ======================
# DATABASE - DEV
# ======================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="pharmacy_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="password"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "connect_timeout": 60,
        }
    }
}

# ======================
# CORS - DEV
# ======================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000", 
    "https://127.0.0.1:3000",
    "http://localhost:4200",  # Ton Angular frontend
    "https://localhost:4200",  # Ton Angular frontend (HTTPS)
    "http://127.0.0.1:4200",
    "https://127.0.0.1:4200",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "http://localhost:8443",
    "https://localhost:8443",  # Au cas où tu changes
    "http://127.0.0.1:8443",
    "https://127.0.0.1:8443",
    "http://167.86.69.173:8000",  # Pour tester le backend distant
    "https://167.86.69.173:8000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # En développement, tout autoriser

# ======================
# CSRF TRUSTED ORIGINS - DEV
# ======================
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://localhost:4200",  # Ton Angular frontend
    "https://localhost:4200",  # Ton Angular frontend (HTTPS)
    "http://127.0.0.1:4200",
    "https://127.0.0.1:4200",
]

# ======================
# SECURITY - DEV (DISABLED)
# ======================
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ======================
# API DOCS - DEVELOPMENT
# ======================
# Garder les API docs activées en développement
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ======================
# LOGGING - DEV
# ======================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.reports': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
