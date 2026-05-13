"""
StreamPlay — Video Streaming Platform
Django settings (development-ready, no external services required).
"""
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-streamplay-change-me-in-production-xxx-123'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
    'corsheaders',

    # Local apps
    'accounts',
    'content',
    'subscriptions',
    'analytics',
    'recommendations',
    'uploads',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# SQLite — tez ishga tushirish uchun (PostgreSQL-ga keyin almashtirish mumkin)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==== DRF ====
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ==== JWT ====
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ==== Swagger / OpenAPI ====
SPECTACULAR_SETTINGS = {
    'TITLE': 'StreamPlay API',
    'DESCRIPTION': (
        "Video on Demand (VOD) platformasi uchun REST API.\n\n"
        "**Xususiyatlari:**\n"
        "- Filmlar, seriallar, epizodlar\n"
        "- Obuna tizimi (SVOD)\n"
        "- Ko'rish tarixi va progress\n"
        "- Qidiruv va tavsiyalar\n"
        "- Chunked fayl yuklash\n"
        "- JWT autentifikatsiya"
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
    },
    'TAGS': [
        {'name': 'auth', 'description': 'Ro\'yxatdan o\'tish, login, JWT token'},
        {'name': 'users', 'description': 'Foydalanuvchi profili'},
        {'name': 'movies', 'description': 'Filmlar'},
        {'name': 'series', 'description': 'Seriallar'},
        {'name': 'seasons', 'description': 'Fasllar'},
        {'name': 'episodes', 'description': 'Epizodlar'},
        {'name': 'genres', 'description': 'Janrlar'},
        {'name': 'actors', 'description': 'Aktyorlar'},
        {'name': 'video-files', 'description': 'Video fayllar va sifat variantlari'},
        {'name': 'subtitles', 'description': 'Subtitrlar'},
        {'name': 'audio-tracks', 'description': 'Audio treklar'},
        {'name': 'subscriptions', 'description': 'Obuna va rejalar'},
        {'name': 'watch-progress', 'description': 'Ko\'rish progressi'},
        {'name': 'history', 'description': 'Ko\'rish tarixi'},
        {'name': 'analytics', 'description': 'Analitika va buffering eventlari'},
        {'name': 'recommendations', 'description': 'Tavsiyalar tizimi'},
        {'name': 'uploads', 'description': 'Chunked fayl yuklash'},
        {'name': 'search', 'description': 'Qidiruv'},
    ],
    'ENUM_NAME_OVERRIDES': {
        'VideoFileStatusEnum': 'content.models.VideoFile.STATUS_CHOICES',
        'SubscriptionStatusEnum': 'subscriptions.models.Subscription.STATUS_CHOICES',
        'PaymentStatusEnum': 'subscriptions.models.Payment.STATUS_CHOICES',
        'UploadStatusEnum': 'uploads.models.Upload.STATUS_CHOICES',
    },
}

# ==== CORS ====
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ==== Cache (LocMem — Redis-ni keyin ulash mumkin) ====
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'streamplay-cache',
    }
}

# ==== Logging (production xatolarni tuta oladigan sozlash) ====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
