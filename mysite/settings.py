"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

########## My custom settings ##########

# Requre HTTPS when transferring sensitive information?
REQUIRE_HTTPS = False

# Use a separate value instead of deriving from the SECRET_KEY, since this isn't really a secret.
# It can even be obtained from the web interface by the admin.
ADMIN_SALT = '5586ae9e10fb6681f37332b26180358b1492dfc990646de79618d33ab3fba597'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h2!94u-kg77+5me^t!=nqwo8tnfb6syjexlk5(0d21xd@2p587'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'ET',
    'misc',
    'pages',
    'notepad',
    'traffic',
    'myadmin',
    'wikihistory',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

APPEND_SLASH = False

DEFAULT_CHARSET = 'utf-8'

FILE_CHARSET = 'utf-8'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "%(asctime)s %(levelname)s %(name)s line %(lineno)3d | %(message)s",
            'datefmt': "%s"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'logging.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/www/logs/django.log',
            'maxBytes': 1000000,
            'backupCount': 99999,
            'formatter': 'standard',
        },
        'sqlfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/www/logs/django_sql.log',
            'maxBytes': 1000000,
            'backupCount': 10,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console', 'logfile'],
            'level':'WARN',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'sqlfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'notepad': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
        'traffic': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
        'myadmin': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
        'misc': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}

########## Read config file settings ##########

# Sensitive or site-specific settings I don't want in version control.
# Put "protected_settings.py" in the BASE_DIR. These will override any settings in this file.
# Credit to Steven Armstrong for idea: https://code.djangoproject.com/wiki/SplitSettings
try:
    from protected_settings import *
except ImportError:
    pass
