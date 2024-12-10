import os
from mongoengine import connect
from decouple import config
from datetime import timedelta

# Base Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]  # Adjust as per your deployment setup.

ROOT_URLCONF = "config.urls"

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_mongoengine",
    "corsheaders",
    "post",  # Your post-service app
]

# Middleware configuration (minimal for MongoEngine)
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be at the top
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # Required by auth
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Cache time to live is 15 minutes (in seconds)
CACHE_TTL = 60 * 15

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "post.authentication.CustomJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "post.permissions.IsAuthenticatedCustom",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,  # Number of records per page
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

# Simple JWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Same as user-service
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # Ensure both services use the same SECRET_KEY
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "username",  # Same as user-service
    "USER_ID_CLAIM": "username",  # Same as user-service
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# MongoDB Configuration
MONGO_DB_NAME = config("MONGO_DB_NAME")
MONGO_HOST = config("MONGO_URI")

#  Connect to MongoDB
connect(db=MONGO_DB_NAME, host=MONGO_HOST)

# Time zone and internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8002",
    "http://54.84.95.41:5173",
    "http://54.84.95.41:8080",
    "http://54.84.95.41:80",
    "http://54.84.95.41:443",
    "http://threadhive.online",
]

CORS_ALLOW_CREDENTIALS = True

# Allow all CORS methods
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Allow all headers
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
