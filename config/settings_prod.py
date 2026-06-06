from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['medex1447.pythonanywhere.com']

# Статика
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Медиа
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/medex1447/library.db',
    }
}

SECRET_KEY = 'django-insecure-)-*qtw3i@qulajkl04oni!k)uwer)p(-3##9_2rb5#!-g5=ys4'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True