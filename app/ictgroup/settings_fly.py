"""
Configuration Django pour Fly.io
"""
import os
from .settings import *

# Configuration Fly.io
DEBUG = False

# Autoriser le domaine Fly.io et ictgroup.fr
ALLOWED_HOSTS = [
    'ictgroup-website.fly.dev',
    '.fly.dev',
    'ictgroup.fr',
    'www.ictgroup.fr',
    'localhost',
    '127.0.0.1'
]

# Middleware avec WhiteNoise pour les fichiers statiques
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Pour servir les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Base de données - Utiliser Supabase PostgreSQL (URL corrigée)
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuration Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Configuration des fichiers statiques pour Fly.io
STATIC_URL = '/static/'
STATIC_ROOT = '/code/app/staticfiles'

# Répertoires des fichiers statiques
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'extranet', 'static'),
    os.path.join(BASE_DIR, 'vitrine', 'static'),
]

# Configuration pour WhiteNoise (servir les fichiers statiques)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configuration WhiteNoise pour Fly.io
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Logging pour Fly.io
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Sécurité
SECURE_SSL_REDIRECT = False  # Fly.io gère SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
