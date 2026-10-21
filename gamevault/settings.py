"""
Configuración de GameVault (Django).

Basada en el proyecto tienda_online: Django REST Framework + SimpleJWT + MySQL.
Las claves y contraseñas NO están en el código: se leen del archivo .env.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.csp import CSP
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Variables de entorno (.env excluido de Git)
load_dotenv(BASE_DIR / '.env')


def env(nombre, default=None):
    return os.environ.get(nombre, default)


SECRET_KEY = env('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('Define DJANGO_SECRET_KEY en el archivo .env')

JWT_SECRET = env('JWT_SECRET', '')
if len(JWT_SECRET) < 32:
    raise ImproperlyConfigured('Define JWT_SECRET (mínimo 32 caracteres) en el archivo .env')

RAWG_API_KEY = env('RAWG_API_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = env('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
]

OWN_APPS = [
    'usuarios',
    'juegos',
]

INSTALLED_APPS = BASE_APPS + THIRD_APPS + OWN_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csp.ContentSecurityPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gamevault.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gamevault.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        # Backend MySQL propio que acepta MySQL 8.0 (ver gamevault/mysql/base.py)
        'ENGINE': 'gamevault.mysql',
        'NAME': env('DB_NAME', 'gamevault'),
        'USER': env('DB_USER', 'root'),
        'PASSWORD': env('DB_PASSWORD', ''),
        'HOST': env('DB_HOST', 'localhost'),
        'PORT': env('DB_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Phoenix'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# El frontend vive en /public y se sirve desde gamevault/views.py

STATIC_URL = 'static/'
PUBLIC_DIR = BASE_DIR / 'public'


# Seguridad
# https://docs.djangoproject.com/en/6.1/topics/security/

# Content Security Policy: solo scripts y estilos propios; imágenes de RAWG
SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF],
    'style-src': [CSP.SELF],
    'img-src': [CSP.SELF, 'data:', 'https://media.rawg.io'],
    'connect-src': [CSP.SELF],
    'object-src': [CSP.NONE],
    'frame-ancestors': [CSP.NONE],
}
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# Evita cuerpos de petición gigantes (10 KB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024


# Django REST Framework
# https://www.django-rest-framework.org/api-guide/settings/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'usuarios.authentication.CookieJWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'auth': '20/15m',   # login/registro: contra fuerza bruta
        'rawg': '60/m',     # proxy hacia la API externa
    },
    'EXCEPTION_HANDLER': 'gamevault.excepciones.manejador_errores',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'SIGNING_KEY': JWT_SECRET,
    'ALGORITHM': 'HS256',
}

# Cookie donde viaja el JWT: httpOnly (JS no puede leerla) y SameSite=Strict (CSRF)
JWT_COOKIE = {
    'key': 'token',
    'httponly': True,
    'samesite': 'Strict',
    'secure': env('COOKIE_SECURE', 'False') == 'True',  # True cuando se use HTTPS
    'max_age': int(SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
}
