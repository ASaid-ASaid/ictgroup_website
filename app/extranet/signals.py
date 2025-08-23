"""
Signaux Django pour l'invalidation automatique du cache.
Se déclenche lors de la création, modification ou suppression des demandes.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache_managers import OptimizedLeaveManager, OptimizedMonthlyReportManager
from .models import LeaveRequest, TeleworkRequest

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LeaveRequest)
def invalidate_leave_cache_on_save(sender, instance, **kwargs):
    """
    Invalide le cache des soldes de congés et rapports mensuels
    quand une demande de congé est créée ou modifiée.
    """
    try:
        # Invalider le cache des soldes pour l'année en cours et précédente
        current_year = instance.start_date.year
        OptimizedLeaveManager.invalidate_cache(instance.user, current_year)
        OptimizedLeaveManager.invalidate_cache(instance.user, current_year - 1)

        # Invalider le cache des rapports mensuels pour les mois concernés
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        # Invalider tous les mois entre start et end
        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            OptimizedMonthlyReportManager.invalidate_cache(
                instance.user, current_year, current_month
            )

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Cache invalidé pour {instance.user.username} suite à modification congé {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur invalidation cache congé: {e}")


@receiver(post_delete, sender=LeaveRequest)
def invalidate_leave_cache_on_delete(sender, instance, **kwargs):
    """
    Invalide le cache quand une demande de congé est supprimée.
    """
    try:
        # Invalider le cache des soldes pour l'année en cours et précédente
        current_year = instance.start_date.year
        OptimizedLeaveManager.invalidate_cache(instance.user, current_year)
        OptimizedLeaveManager.invalidate_cache(instance.user, current_year - 1)

        # Invalider le cache des rapports mensuels pour les mois concernés
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        # Invalider tous les mois entre start et end
        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            OptimizedMonthlyReportManager.invalidate_cache(
                instance.user, current_year, current_month
            )

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Cache invalidé pour {instance.user.username} suite à suppression congé {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur invalidation cache suppression congé: {e}")


@receiver(post_save, sender=TeleworkRequest)
def invalidate_telework_cache_on_save(sender, instance, **kwargs):
    """
    Invalide le cache des rapports mensuels quand une demande de télétravail
    est créée ou modifiée.
    """
    try:
        # Invalider le cache des rapports mensuels pour les mois concernés
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        # Invalider tous les mois entre start et end
        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            OptimizedMonthlyReportManager.invalidate_cache(
                instance.user, current_year, current_month
            )

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Cache rapport mensuel invalidé pour {instance.user.username} suite à modification télétravail {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur invalidation cache télétravail: {e}")


@receiver(post_delete, sender=TeleworkRequest)
def invalidate_telework_cache_on_delete(sender, instance, **kwargs):
    """
    Invalide le cache quand une demande de télétravail est supprimée.
    """
    try:
        # Invalider le cache des rapports mensuels pour les mois concernés
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        # Invalider tous les mois entre start et end
        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            OptimizedMonthlyReportManager.invalidate_cache(
                instance.user, current_year, current_month
            )

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Cache rapport mensuel invalidé pour {instance.user.username} suite à suppression télétravail {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur invalidation cache suppression télétravail: {e}")
