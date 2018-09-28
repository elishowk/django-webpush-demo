"""
Django settings for djangowebpushpoc project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'teemdhizby)!w&y3)sgsaaqvwelttha=iq&5#bfzqm%9hugdbl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'push_notifications',
    'webpush',
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

ROOT_URLCONF = 'djangowebpushpoc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'djangowebpushpoc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# How-to configure VAPID
#   $ pip install pywebpush py-vapid
# * Create a temporary file (claim.json) like this:
#
#   {
#     "sub": "mailto: android@entrouvert.com",
#     "aud": "https://fcm.googleapis.com"
#   }
#
# * Generate public and private keys:
#
#   $ vapid --sign claim.json
#
# * Generate client public key (applicationServerKey)
#
#   $ vapid --applicationServerKey
#
#       Application Server Key = BEFuGfKKEFp-kEB...JlkA34llWF0xHya70
#
# * Configure settings:
# ** ``APP_SERVER_KEY``: Copy the value output of the previous command to your local_settings.py or to the multinenant configuration combo_settings.py
# ** do not touch WP_CLAIMS

PUSH_NOTIFICATIONS_SETTINGS = {
    'WP_PRIVATE_KEY': os.path.join(BASE_DIR, "private_key.pem"), # file generated by the vapid command (from py-vapid)
    'WP_CLAIMS': {
        "sub": "mailto: elias@showk.me" # 'sub' *must* be the only item, do not touch this, you could break VAPID protocol
    },
    'WP_ERROR_TIMEOUT': 10, # timeout for the request on the push server
    'UPDATE_ON_DUPLICATE_REG_ID': True,
}

local_settings_file = os.path.join(os.path.dirname(__file__), 'local_settings.py')

if os.path.exists(local_settings_file):
    exec(open(local_settings_file).read())