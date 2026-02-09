"""
Base settings for Pharmacy Backend
Common settings shared across environments
"""
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# CORE SETTINGS
# ======================
# SECRET_KEY must be set via environment variable
SECRET_KEY = config("SECRET_KEY")  # NO DEFAULT - forces environment variable

DEBUG = config("DEBUG", default=False, cast=bool)

# Validate SECRET_KEY on startup
import secrets
import string

def validate_secret_key(key: str) -> bool:
    """Validate that SECRET_KEY is strong enough"""
    if len(key) < 50:
        return False
    if not any(c in string.ascii_letters + string.digits + string.punctuation for c in key):
        return False
    if key in ['django-insecure-dev-key', 'your-secret-key-here']:
        return False
    return True

if not validate_secret_key(SECRET_KEY):
    raise ValueError(
        "SECRET_KEY is too weak or using default value. "
        "Generate a strong key: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
    )

# ======================
# APPLICATIONS
# ======================
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "corsheaders",

    # Local apps
    "apps.accounts",
    "apps.suppliers",
    "apps.invoices",
    "apps.credit_notes",
    "apps.reports",
    "apps.health",
]

# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ======================
# DJANGO REST FRAMEWORK
# ======================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
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
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ======================
# URL / TEMPLATES
# ======================
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "config" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ======================
# AUTH
# ======================
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ======================
# INTERNATIONALIZATION
# ======================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ======================
# STATIC & MEDIA
# ======================
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ======================
# DEFAULT FIELD
# ======================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
