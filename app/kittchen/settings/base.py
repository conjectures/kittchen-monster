"""
Django settings for kittchen project.
"""

import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
# ROOT_DIR = os.path.dirname(APP_DIR)

# print(f"{BASE_DIR=}")
# print(f"{ROOT_DIR=}")


env = environ.Env()
# environ.Env.read_env(os.path.join(ROOT_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# False if not in os.environ
DEBUG = env('DEBUG')

# Raise ImporperlyConfigured exception if not in os.environ
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.str('DJANGO_ALLOWED_HOSTS', default='*').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ordered_model',
    'rest_framework',
    'kittchen.core',
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

ROOT_URLCONF = 'kittchen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'kittchen.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
        'default': env.db(),

}
#             'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     },
# }
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'django_app',
#         'USER': 'django_user',
#         'PASSWORD': 'BXsWTAbt9qfaHOgHMWdWc6Ntw',
#         # hostname equivalent to ip for docker-compose container networking
#         'HOST': 'mariadb',
#         'PORT': '3306',
#     },
# }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# REST_FRAMEWORK = {
#         # Use Django's standard 'django.contrib.auth' permissions,
#         # or allow read-only access for anauthenticated users.
#         'DEFAULT_PERMISSION_CLASSES': [
#             'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
#             ],
#         'DEFAULT_THROTTLE_CLASSES': [
#             'rest_framework.throttling.AnonRateThrottle',
#             'rest_framework.thorttling.UserRateThrottle',
#             ],
#         'DEFAULT_THROTTLE_RATES': {
#             'anon': '100/day',
#             'user': '1000/day'
#             }
#         }


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-uk'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

CORE_DIR = os.path.join(BASE_DIR, 'core')


STATIC_URL = '/static/'
STATIC_ROOT = "/static_files/"

STATICFILES_DIRS = (
        os.path.join(CORE_DIR, 'static'),
        )



MEDIA_URL = '/media/'
MEDIA_ROOT = (
        os.path.join(BASE_DIR, 'media')
        )

LOGIN_URL = 'login'
# LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
