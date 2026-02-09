"""
Staging settings - simple configuration for debugging
"""
from .settings_base import *
import os
import dj_database_url

print("=== SETTINGS STAGING CHARGÉ ===")
print(f"DJANGO_ENVIRONMENT: {os.environ.get('DJANGO_ENVIRONMENT')}")

# Staging configuration
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database configuration for staging
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

# CORS simple
CORS_ALLOWED_ORIGINS = [
    'http://167.86.69.173',
    'https://167.86.69.173',
    'http://localhost:3000',
    'http://localhost:4200'
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False

# Middleware simplifié
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

print(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
print(f"DATABASE ENGINE: {DATABASES['default']['ENGINE']}")
print("==============================")
