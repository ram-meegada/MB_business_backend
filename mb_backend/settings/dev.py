from .base import *


DEBUG = True

MIDDLEWARE += ['mb_backend.customMiddleware.QueriesCounterMiddleware']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'MB_Backend',
        'USER': 'postgres',
        'PASSWORD': 'Ramu@123',
        'HOST': '127.0.0.1',
        'PORT': 5432
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # "ROTATE_REFRESH_TOKENS": True,
    # "BLACKLIST_AFTER_ROTATION": True
}

COOKIE_SECURE = False
SAME_SITE = 'Lax'
