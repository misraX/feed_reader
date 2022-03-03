"""
Django settings for feed_reader project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os.path
from pathlib import Path

import environ

root = environ.Path(__file__) - 2
env = environ.Env(
    DEBUG=(bool, False),
    DJANGO_LOG_LEVEL=(str, 'INFO'),
)
env.read_env(f'{root}/.env')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'django_celery_results',
    'drf_yasg',
    'knox',
    'apps.accounts',
    'apps.feed',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'log_request_id.middleware.RequestIDMiddleware',
]

ROOT_URLCONF = 'feed_reader.urls'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(f'{BASE_DIR}/logs', 'app-messages')
DEFAULT_FROM_EMAIL = 'noreply@email.com'
ADMINS = [('misrax', 'misrax.user@email.com')]
AUTH_USER_MODEL = 'accounts.User'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'feed_reader.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': env.db(),
    'extra': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}
SWAGGER_SETTINGS = {
    'DEFAULT_API_URL': 'http://localhost',
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
}
# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter',
        },
    },
    'formatters': {
        'file_handler_formatter': {
            'format': '%(levelname)s [%(asctime)s] [%(request_id)s] [%(filename)s->%(funcName)s():%(lineno)s]'
                      ' [%(name)s] %(message)s',
        },
    },
    'handlers': {
        'request_logging': {
            'level': 'DEBUG',
            'formatter': 'file_handler_formatter',
            'class': 'logging.FileHandler',
            'filters': ['request_id'],
            'filename': os.path.join(f'{BASE_DIR}/logs', 'requests.log'),
        },
        'feed_parser': {
            'level': 'INFO',
            'formatter': 'file_handler_formatter',
            'class': 'logging.FileHandler',
            'filters': ['request_id'],
            'filename': os.path.join(f'{BASE_DIR}/logs', 'feed_parser.log'),
        },
        'celery': {
            'level': 'INFO',
            'formatter': 'file_handler_formatter',
            'class': 'logging.FileHandler',
            'filters': ['request_id'],
            'filename': os.path.join(f'{BASE_DIR}/logs', 'celery.log'),
        },
        'info': {
            'level': 'DEBUG',
            'formatter': 'file_handler_formatter',
            'class': 'logging.FileHandler',
            'filters': ['request_id'],
            'filename': os.path.join(f'{BASE_DIR}/logs', 'info.log'),
        },
    },
    'loggers': {
        '': {
            'handlers': ['info'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_logging'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['request_logging'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'feed_parser': {
            'handlers': ['feed_parser'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            'handlers': ['celery'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': env.str('CACHE_LOCATION'),
    },
}
# TESTING
TEST_RUNNER = 'feed_reader.test_runner.Runner'

# CELERY
# Celery Configuration Options
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
# CELERY_TASK_ALWAYS_EAGER = True

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'

# REQUEST TRACING

LOG_REQUEST_ID_HEADER = 'HTTP_X_REQUEST_ID'
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = 'HTTP_X_FEED_READER_ID'
