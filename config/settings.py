

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
    'app_accounting',
    'app_history',
    'app_global',

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


LOGS_DIR = BASE_DIR / 'logs'  # Создаем путь к папке logs в корне проекта
LOGS_DIR.mkdir(parents=True, exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} [{process:d}:{thread:d}] {message}',
            'style': '{',
        },
        'simple_time_message': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': { # Оставим вывод в консоль для удобства отладки, если понадобится
            'level': 'DEBUG', # В консоль можно выводить и DEBUG для отладки
            'class': 'logging.StreamHandler',
            'formatter': 'simple_time_message',
        },
        'app_log_file_daily': { # Для ваших логов приложения
            'level': 'INFO',     # Минимальный уровень для ваших логов
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGS_DIR / 'app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,    # Хранить логи за 7 дней
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'error_log_file_daily': { # Для всех ошибок
            'level': 'ERROR',    # Только ошибки и критические сообщения
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,   # Хранить ошибки за 30 дней
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'app_productions': {
            'handlers': ['app_log_file_daily', 'error_log_file_daily'], # Ваши логи в app.log, ошибки также в errors.log
            'level': 'INFO', # Писать INFO и выше от вашего приложения
            'propagate': False, # Не передавать сообщения родительским логгерам
        },
        # Логгер для самого Django
        'django': {
            'handlers': ['error_log_file_daily'], # Ошибки Django пойдут в errors.log
            'level': 'ERROR', # Обрабатывать только ERROR и CRITICAL от Django
            'propagate': False, # Не обязательно, но можно оставить False
        },
        # Логгер для ошибок запросов Django (4XX, 5XX)
        'django.request': {
            'handlers': ['error_log_file_daily'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Можно добавить логгер для ошибок базы данных, если нужно их отдельно отслеживать
        'django.db.backends': {
            'handlers': ['error_log_file_daily'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Если вы хотите разные уровни логирования в зависимости от DEBUG
# if DEBUG:
#     LOGGING['loggers']['django']['level'] = 'DEBUG'
#     LOGGING['loggers']['app_productions']['level'] = 'DEBUG'
#     # Можно переопределить и другие уровни для хендлеров или логгеров
# else:
#     LOGGING['loggers']['django']['level'] = 'INFO'
#     LOGGING['loggers']['app_productions']['level'] = 'INFO'