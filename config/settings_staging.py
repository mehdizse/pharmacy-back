"""
Staging settings - simple configuration for debugging
"""
from .settings_base import *
import os

print("=== SETTINGS STAGING CHARGÉ ===")
print(f"DJANGO_ENVIRONMENT: {os.environ.get('DJANGO_ENVIRONMENT')}")

# Staging configuration
DEBUG = True
ALLOWED_HOSTS = ['*']

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
print("==============================")
