from skill_match.settings import *

SECRET_KEY = 'vwn2!7ow-@azz(l#69k15&b15#)w4%b1f62m_8o&*s!clw(tk$'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'skill_match',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': ''
    }
}

LOGGING = None