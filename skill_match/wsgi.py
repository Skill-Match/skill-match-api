"""
WSGI config for skill_match project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
from dj_static import Cling

import os

from django.core.wsgi import get_wsgi_application

# os.environ['DJANGO_SETTINGS_MODULE'] = 'skill_match.settings'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skill_match.settings")

application = Cling(get_wsgi_application())
