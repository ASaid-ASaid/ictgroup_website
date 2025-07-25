"""
Paramètres principaux de l'application Django ICTGROUP.
- Les variables sensibles (SECRET_KEY, DB, etc.) sont chargées depuis les variables d'environnement.
- Adaptez ce fichier pour la production (DEBUG, ALLOWED_HOSTS, etc.).
"""

"""
Paramètres de Django pour le projet ICTGROUP.
Généré par 'django-admin startproject' en utilisant Django 4.2.
Ce fichier contient la configuration principale du projet.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Construit les chemins à l'intérieur du projet comme ceci : BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Clé secrète Django.
# À garder secrète en production ! Utilisez une variable d'environnement.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-default-key-for-dev-only')


# Mode de débogage.
# À désactiver en production !
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Hôtes autorisés.
# En production, listez votre nom de domaine (ex: .ictgroup.fr) et le domaine Fly.io.
ALLOWED_HOSTS = ['*'] if DEBUG else ['.ictgroup.fr', '.fly.dev', 'localhost', '127.0.0.1']


# Applications installées.
# Ajoutez vos applications ici.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vitrine',  # Application pour la partie publique
    'extranet', # Application pour l'extranet employés
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

ROOT_URLCONF = 'ictgroup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Dossier global pour les templates si nécessaire
        'APP_DIRS': True, # Permet à Django de chercher les templates dans les dossiers 'templates' des applications
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

WSGI_APPLICATION = 'ictgroup.wsgi.application'


# Configuration de la base de données PostgreSQL via DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# Configuration du mot de passe
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


# Internationalisation
LANGUAGE_CODE = 'fr-fr' # Langue française

TIME_ZONE = 'Europe/Paris' # Fuseau horaire de Paris

USE_I18N = True

USE_TZ = True


# Fichiers statiques (CSS, JavaScript, images)
STATIC_URL = '/static/'
# Chemin où collecter les fichiers statiques en production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Type de champ de clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL de redirection après connexion
LOGIN_REDIRECT_URL = '/extranet/demandes/'
# URL de connexion
LOGIN_URL = '/extranet/login/'

# Configuration du logging pour tracer les actions et erreurs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Ajoutez ici d'autres loggers personnalisés si besoin
    },
}
