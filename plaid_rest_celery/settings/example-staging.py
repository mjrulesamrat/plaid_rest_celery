from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sherlocked'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
    }
}


TIME_ZONE = 'Asia/Calcutta'

USE_TZ = True
