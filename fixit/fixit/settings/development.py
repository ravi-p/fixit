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
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'fixit.db'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_fixit',
        'USER': 'colama',
        'PASSWORD': 'coriolis',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

# The callable to use to configure logging
LOGGING_CONFIG = 'logging.config.dictConfig'

# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        #'taskq_http_formater':{
        #    'format':'%(name)s - %(levelname)8s - %(message)s'
        #},
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'fixit.log',
            'formatter': 'verbose'
        },
        #'taskq_http_handler':{
        #    'level':'DEBUG',
        #    'class':'logging.handlers.HTTPHandler(host,url,method='GET')',
        #    'formatters':'taskq_http_formater',

        #},
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'taskq': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },

        #'taskq_http':{
        #    'handlers':['taskq_http_handler'],
        #    'level':'DEBUG',
        #},

    }
}


