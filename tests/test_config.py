#!/usr/bin/env python3
"""
Configuration des tests pour l'application ICTGROUP Website
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire de l'application au path Python
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

# Configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ictgroup.settings")

import django

django.setup()

# Configuration des tests
TEST_SETTINGS = {
    "DATABASE": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "DEBUG": False,
    "PASSWORD_HASHERS": [
        "django.contrib.auth.hashers.MD5PasswordHasher",  # Hasher rapide pour les tests
    ],
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    },
}
