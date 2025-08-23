"""
Configuration de l'application extranet.
"""

from django.apps import AppConfig


class ExtranetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "extranet"
    verbose_name = "Extranet ICT Group"

    def ready(self):
        """
        Méthode appelée quand l'application est prête.
        Importe les signaux pour l'invalidation automatique du cache.
        """
        try:
            import extranet.signals
        except ImportError:
            pass
