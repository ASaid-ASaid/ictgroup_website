"""Django settings for the ICTGROUP project.

Sensitive values (SECRET_KEY, database URLs) are loaded from environment
variables. Adjust DEBUG and ALLOWED_HOSTS for production.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Construit les chemins à l'intérieur du projet comme ceci : BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Clé secrète Django.
# À garder secrète en production ! Utilisez une variable d'environnement.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-default-key-for-dev-only")


# Mode de débogage.
# À désactiver en production !
DEBUG = os.getenv("DEBUG", "False") == "True"

# Hôtes autorisés.
# En production, listez votre nom de domaine (ex: .ictgroup.fr) et le domaine Fly.io.
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [
        "ictgroup-website.fly.dev",
        ".fly.dev",
        "ictgroup.fr",
        "www.ictgroup.fr",
        "localhost",
        "127.0.0.1",
    ]


# Applications installées.
# Ajoutez vos applications ici.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "vitrine",  # Application pour la partie publique
    "extranet",  # Application pour l'extranet employés
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Pour servir fichiers statiques en production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ictgroup.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        # Permet à Django de chercher les templates dans les dossiers 'templates' des applications
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "extranet.context_processors.validation_context",
                "extranet.context_processors.document_context",
            ],
        },
    },
]

WSGI_APPLICATION = "ictgroup.wsgi.application"


# Configuration de la base de données PostgreSQL via DATABASE_URL
DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}

# Optimisations base de données (seulement si on n'est pas sur Docker/Supabase)
if not os.getenv("DATABASE_URL", "").startswith("postgresql://"):
    DATABASES["default"]["CONN_MAX_AGE"] = 600  # 10 minutes
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# Configuration du cache Redis (fallback vers cache local si Redis indisponible)
REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL and not DEBUG:
    # Production avec Redis
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 50,
                    "retry_on_timeout": True,
                },
            },
            "KEY_PREFIX": "ictgroup",
            "TIMEOUT": 300,  # 5 minutes par défaut
        }
    }
    
    # Sessions en cache Redis
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    # Développement avec cache local
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ictgroup-cache",
            "TIMEOUT": 300,
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
            }
        }
    }

SESSION_COOKIE_AGE = 3600  # 1 heure

# Configuration du mot de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalisation
LANGUAGE_CODE = "fr-fr"  # Langue française

TIME_ZONE = "Europe/Paris"  # Fuseau horaire de Paris

USE_I18N = True

USE_TZ = True


# Fichiers statiques (CSS, JavaScript, images)
STATIC_URL = "/static/"
# Chemin où collecter les fichiers statiques en production
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Configuration pour WhiteNoise (servir les fichiers statiques)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Répertoires des fichiers statiques
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "extranet", "static"),
    os.path.join(BASE_DIR, "vitrine", "static"),
]

# Configuration supplémentaire pour la production
if not DEBUG:
    # Force HTTPS pour les fichiers statiques en production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

    # Configuration WhiteNoise plus agressive
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

# Type de champ de clé primaire par défaut
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URL de redirection après connexion
LOGIN_REDIRECT_URL = "/extranet/"
# URL de connexion
LOGIN_URL = "/extranet/login/"

# Configuration du logging pour tracer les actions et erreurs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "performance": {
            "format": "[{asctime}] PERF {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "django.log"),
            "formatter": "verbose",
        },
        "performance_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "performance.log"),
            "formatter": "performance",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING" if not DEBUG else "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING" if not DEBUG else "INFO",
            "propagate": False,
        },
        "extranet": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "performance": {
            "handlers": ["performance_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Optimisations de performance supplémentaires
if not DEBUG:
    # Optimisations production
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_FRAME_DENY = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    
    # Compression Gzip
    MIDDLEWARE.insert(1, 'django.middleware.gzip.GZipMiddleware')
    
    # Cache control
    MIDDLEWARE.append('django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE.append('django.middleware.common.CommonMiddleware')
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')
    
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
    CACHE_MIDDLEWARE_KEY_PREFIX = 'ictgroup_cache'

# Configuration pour les uploads de fichiers
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Limites d'upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Optimisations des requêtes
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Settings pour éviter les requêtes N+1
SELECT_RELATED_FIELDS = ['user', 'user__profile']
PREFETCH_RELATED_FIELDS = ['user__leave_requests', 'user__telework_requests']
