from .settings import *

DEBUG = True
SECRET_KEY = os.environ['SECRET_KEY']

BLACKLIST = ['debug_toolbar', 'django_extensions']
INSTALLED_APPS = tuple([app for app in INSTALLED_APPS if app not in BLACKLIST])

import dj_database_url
DATABASES['default'] =  dj_database_url.config()
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIR = (
    os.path.join(BASE_DIR, 'static')
)

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
TOKEN = os.environ['TOKEN']
TOKEN_SECRET = os.environ['TOKEN_SECRET']

# SENDGRID_KEY = os.environ['SENDGRID_KEY']

# TWILIO_SID = os.environ['TWILIO_SID']
# TWILIO_TOKEN = os.environ['TWILIO_TOKEN']
