

from datetime import timedelta
from pathlib import Path
from decouple import config
import os


######################################################################
# Unfold
######################################################################

# noinspection PyUnresolvedReferences
from config.custom_theme.theme_settings import UNFOLD

UNFOLD = UNFOLD

######################################################################
# General
######################################################################
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG")
ALLOWED_HOSTS = ['*']
WSGI_APPLICATION = 'config.wsgi.application'
ROOT_URLCONF = 'config.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
######################################################################
# Apps
######################################################################
INSTALLED_APPS = [
    "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #lib
    'rest_framework',
    'rest_framework_simplejwt',
    #app
    'app_users',
    'app_productions',
    # 'app_packaging',
    # 'app_utug',
    # 'app_tailor',
    'app_history',
    # 'app_croi',
    # 'app_logistics',

    # 'app_accounting',
    # 'app_analytics',
]


######################################################################
# Middleware
######################################################################
MIDDLEWARE = [
    "simple_history.middleware.HistoryRequestMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
######################################################################
# Templates
######################################################################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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


######################################################################
# Database
######################################################################
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": config("POSTGRES_USER", "postgres"),
        "PASSWORD": config("POSTGRES_PASSWORD", "postgres"),
        "NAME": config("POSTGRES_DB", "chveya"),
        "HOST": config("POSTGRES_HOST", "db"),
        "PORT": "5432",
        "TEST": {
            "NAME": "test",
        },
    }
}
######################################################################
# Authentication
######################################################################

AUTH_USER_MODEL = "app_users.User"

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:89899",
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

######################################################################
# Internationalization
######################################################################

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True


######################################################################
# Staticfiles
######################################################################
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Collect static files into this directory
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Path to additional static files (excluding static_root)
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
######################################################################
# Rest Framework
######################################################################
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=60),
}


# import django
# from .auto_create_start.create_pier_user import SettingsFactory
# django.setup()
# settings_users_pier = SettingsFactory().create_all()