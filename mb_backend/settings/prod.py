from .base import *


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mb_backend_render_db',
        'USER': 'mb_backend_render_db_user',
        'PASSWORD': 'smbcaKeuLNALRPHNzesedyeC2NGKuz5H',
        'HOST': 'dpg-d2balridbo4c73alhpbg-a.singapore-postgres.render.com',
        'PORT': 5432
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # "ROTATE_REFRESH_TOKENS": True,
    # "BLACKLIST_AFTER_ROTATION": True
}
