# -*- coding: utf-8 -*-
from .base import *

DEBUG = True 
TEMPLATE_DEBUG = DEBUG


GOOGLE_OAUTH2_CLIENT_ID='1077258824046-lsb9thgrb61tlb0mamd2v4spaedvuot7.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET='9rNLn87nP8gkhi6qFr88sjLs'

STATICFILES_DIRS = (os.path.join(BASE, "static"),)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_fixit',
        'USER': 'postgres',
        'PASSWORD': 'coriolis',
        'HOST': 'fixit',
        'PORT': '5432',
    }
}


