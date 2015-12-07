import os
import random
import socket

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = [] # add your host name in local/settings.py

BASE_DIR = os.path.dirname(__file__)
LOCAL_DIR = os.path.join(BASE_DIR, 'local')

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core',
    'apps.roster',
)

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'content'),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = False
USE_L10N = False
USE_TZ = False

if not hasattr(globals(), 'SECRET_KEY'):
    secret_file = os.path.join(LOCAL_DIR, 'secret_key.txt')
    try:
        SECRET_KEY = open(secret_file).read().strip()
    except IOError:
        try:
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+'
            SECRET_KEY = ''.join([random.choice(chars) for i in range(50)])
            if not os.path.isdir(LOCAL_DIR):
                os.mkdir(LOCAL_DIR)
            secret = file(secret_file, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            raise Exception('Please create file {} filled with random characters to serve as your secret key.'.format(secret_file))
    del secret_file

try:
    from local.settings import *
except ImportError:
    pass

