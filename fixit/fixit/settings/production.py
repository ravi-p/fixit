# -*- coding: utf-8 -*-
from .base import *

DEBUG = False 
TEMPLATE_DEBUG = DEBUG

GOOGLE_OAUTH2_CLIENT_ID='954877994637-ut32rg4kd31tf4ea85i8t3i4hdp7cf28.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET='oIHMIDDnxCbTkkewKeC3wbBS'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')



# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'fixit.db'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fixit',
        'USER': 'colama',
        'PASSWORD': 'coriolis',
        'HOST': 'localhost',
        'PORT': '',
    }
}
