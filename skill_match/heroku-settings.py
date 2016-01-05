from .settings import *

DEBUG = False
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

YELP_CONSUMER_KEY = os.environ['YELP_CONSUMER_KEY']
YELP_CONSUMER_SECRET = os.environ['YELP_CONSUMER_SECRET']
YELP_TOKEN = os.environ['YELP_TOKEN']
YELP_TOKEN_SECRET = os.environ['YELP_TOKEN_SECRET']

SENDGRID_KEY = os.environ['SENDGRID_KEY']

TWILIO_SID = os.environ['TWILIO_SID']
TWILIO_TOKEN = os.environ['TWILIO_TOKEN']

cloudinary.config(
  cloud_name=os.environ['CLOUD_NAME'],
  api_key=os.environ['CLOUDINARY_KEY'],
  api_secret=os.environ['CLOUDINARY_SECRET']
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        }
    },
    'handlers': {
        'mailer': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'api': {
            'handlers': ['console', 'mailer'],
            'level': 'DEBUG',
            'propagate': True
        }
    },
}