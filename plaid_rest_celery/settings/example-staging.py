from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "sherlocked")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", False)

# Allowed hosts who can connect with Django app
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", False)


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        # "ENGINE": 'django_prometheus.db.backends.sqlite3',
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

# time zone settings
TIME_ZONE = 'Asia/Calcutta'

USE_TZ = True

# celery and broker configurations
BROKER_USER = os.environ.get("BROKER_USER", "plaidrabbitadmin")
BROKER_PASSWORD = os.environ.get("BROKER_PASSWORD", "password")
BROKER_HOST = os.environ.get("BROKER_HOST", "0.0.0.0")
BROKER_PORT = os.environ.get("BROKER_PORT", "5672")
BROKER_VHOST = os.environ.get("BROKER_VHOST", "/")

CELERY_BROKER_URL = f"amqp://{BROKER_USER}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}/{BROKER_VHOST}"

# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = os.environ.get("TIME_ZONE", "Asia/Calcutta")

# Plaid configurations
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DNS'),
    integrations=[DjangoIntegration(), CeleryIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = "mjrulesamrat@gmail.com"

# API CORS Allow all for now
CORS_ORIGIN_ALLOW_ALL = True

# DJOSER config
DJOSER = {
    'SEND_ACTIVATION_EMAIL': False,
}
