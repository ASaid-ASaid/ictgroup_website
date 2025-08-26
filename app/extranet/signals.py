"""
Signaux Django pour la mise à jour automatique des soldes et statistiques.
Se déclenche lors de la création, modification ou suppression des demandes.
"""

import logging
from datetime import date
from decimal import Decimal

from django.db.models.signals import post_delete, post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import LeaveRequest, TeleworkRequest, OverTimeRequest, UserLeaveBalance, MonthlyUserStats

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LeaveRequest)
def update_leave_balances_on_save(sender, instance, **kwargs):
    """
    Met à jour les soldes de congés et statistiques mensuelles
    quand une demande de congé est créée ou modifiée.
    """
    try:
        # Mettre à jour le solde de congés de l'utilisateur
        today = date.today()
        
        # Déterminer la période de congés
        if today.month >= 6:  # juin à décembre
            period_start = date(today.year, 6, 1)
        else:  # janvier à mai
            period_start = date(today.year - 1, 6, 1)
        
        try:
            balance = UserLeaveBalance.objects.get(
                user=instance.user,
                period_start=period_start
            )
            balance.update_taken_days()
        except UserLeaveBalance.DoesNotExist:
            logger.warning(f"Aucun solde trouvé pour {instance.user.username} période {period_start}")

        # Mettre à jour les statistiques mensuelles pour les mois concernés
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        # Mettre à jour tous les mois entre start et end
        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            stats, created = MonthlyUserStats.objects.get_or_create(
                user=instance.user,
                year=current_year,
                month=current_month
            )
            stats.update_from_requests()

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Soldes et statistiques mis à jour pour {instance.user.username} suite à modification congé {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour soldes/statistiques congé: {e}")


@receiver(post_delete, sender=LeaveRequest)
def update_leave_balances_on_delete(sender, instance, **kwargs):
    """
    Met à jour les soldes et statistiques quand une demande de congé est supprimée.
    """
    try:
        # Mettre à jour le solde de congés de l'utilisateur
        today = date.today()
        
        # Déterminer la période de congés
        if today.month >= 6:  # juin à décembre
            period_start = date(today.year, 6, 1)
        else:  # janvier à mai
            period_start = date(today.year - 1, 6, 1)
        
        try:
            balance = UserLeaveBalance.objects.get(
                user=instance.user,
                period_start=period_start
            )
            balance.update_taken_days()
        except UserLeaveBalance.DoesNotExist:
            logger.warning(f"Aucun solde trouvé pour {instance.user.username} période {period_start}")

        # Mettre à jour les statistiques mensuelles
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            try:
                stats = MonthlyUserStats.objects.get(
                    user=instance.user,
                    year=current_year,
                    month=current_month
                )
                stats.update_from_requests()
            except MonthlyUserStats.DoesNotExist:
                pass

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Soldes et statistiques mis à jour pour {instance.user.username} suite à suppression congé {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour soldes/statistiques suppression congé: {e}")


@receiver(post_save, sender=TeleworkRequest)
def update_stats_on_telework_save(sender, instance, **kwargs):
    """
    Met à jour les statistiques mensuelles quand une demande de télétravail est créée ou modifiée.
    """
    try:
        # Mettre à jour les statistiques mensuelles pour les mois concernés
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            stats, created = MonthlyUserStats.objects.get_or_create(
                user=instance.user,
                year=current_year,
                month=current_month
            )
            stats.update_from_requests()

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Statistiques mises à jour pour {instance.user.username} suite à modification télétravail {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour statistiques télétravail: {e}")


@receiver(post_delete, sender=TeleworkRequest)
def update_stats_on_telework_delete(sender, instance, **kwargs):
    """
    Met à jour les statistiques quand une demande de télétravail est supprimée.
    """
    try:
        # Mettre à jour les statistiques mensuelles
        start_month = instance.start_date.month
        start_year = instance.start_date.year
        end_month = instance.end_date.month
        end_year = instance.end_date.year

        current_month = start_month
        current_year = start_year

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            try:
                stats = MonthlyUserStats.objects.get(
                    user=instance.user,
                    year=current_year,
                    month=current_month
                )
                stats.update_from_requests()
            except MonthlyUserStats.DoesNotExist:
                pass

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        logger.info(
            f"Statistiques mises à jour pour {instance.user.username} suite à suppression télétravail {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour statistiques suppression télétravail: {e}")


@receiver(post_save, sender=OverTimeRequest)
def update_stats_on_overtime_save(sender, instance, **kwargs):
    """
    Met à jour les statistiques mensuelles quand une demande d'heures supplémentaires est créée ou modifiée.
    """
    try:
        # Mettre à jour les statistiques mensuelles pour le mois de la demande
        stats, created = MonthlyUserStats.objects.get_or_create(
            user=instance.user,
            year=instance.work_date.year,
            month=instance.work_date.month
        )
        stats.update_from_requests()

        logger.info(
            f"Statistiques mises à jour pour {instance.user.username} suite à modification heures supplémentaires {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour statistiques heures supplémentaires: {e}")


@receiver(post_delete, sender=OverTimeRequest)
def update_stats_on_overtime_delete(sender, instance, **kwargs):
    """
    Met à jour les statistiques quand une demande d'heures supplémentaires est supprimée.
    """
    try:
        # Mettre à jour les statistiques mensuelles
        try:
            stats = MonthlyUserStats.objects.get(
                user=instance.user,
                year=instance.work_date.year,
                month=instance.work_date.month
            )
            stats.update_from_requests()
        except MonthlyUserStats.DoesNotExist:
            pass

        logger.info(
            f"Statistiques mises à jour pour {instance.user.username} suite à suppression heures supplémentaires {instance.id}"
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour statistiques suppression heures supplémentaires: {e}")


@receiver(user_logged_in)
def auto_monthly_leave_accrual_on_login(sender, request, user, **kwargs):
    """
    Lance automatiquement l'accrual mensuel de congés à la première connexion du mois.
    Utilise le cache pour éviter les exécutions multiples.
    """
    try:
        today = date.today()
        cache_key = f"monthly_accrual_{today.year}_{today.month:02d}"
        
        # Vérifier si l'accrual de ce mois a déjà été fait
        if cache.get(cache_key):
            logger.debug(f"Accrual déjà fait ce mois {today.month}/{today.year} - Connexion ignorée")
            return
        
        logger.info(f"🚀 Première connexion du mois {today.month}/{today.year} - Lancement accrual automatique")
        
        # Marquer immédiatement pour éviter les exécutions simultanées
        cache.set(cache_key, True, timeout=30*24*3600)  # 30 jours
        
        # Récupérer tous les utilisateurs actifs avec profil
        users = User.objects.filter(
            is_active=True,
            profile__isnull=False
        ).select_related('profile')
        
        updated_count = 0
        
        for user_obj in users:
            try:
                profile = user_obj.profile
                
                # Déterminer les jours à ajouter selon le site
                site_lower = profile.site.lower() if profile.site else ''
                if site_lower in ['fr', 'france']:
                    monthly_days = Decimal('2.5')
                elif site_lower in ['tn', 'tunisie']:
                    monthly_days = Decimal('1.8')
                else:
                    continue
                
                # Période fiscale du 1er juin au 31 mai
                if today.month >= 6:
                    period_start = date(today.year, 6, 1)
                else:
                    period_start = date(today.year - 1, 6, 1)
                
                period_end = date(period_start.year + 1, 5, 31)
                
                # Récupérer ou créer le solde de congés pour la période courante
                balance, created = UserLeaveBalance.objects.get_or_create(
                    user=user_obj,
                    period_start=period_start,
                    defaults={
                        'days_acquired': Decimal('0'),
                        'days_taken': Decimal('0'),
                        'days_carry_over': Decimal('0'),
                        'period_end': period_end,
                    }
                )
                
                # Ajouter les jours mensuels
                balance.days_acquired += monthly_days
                balance.save()
                
                updated_count += 1
                logger.info(f"✅ Accrual automatique: {user_obj.username} ({profile.site}) +{monthly_days} jours")
                
            except Exception as e:
                logger.error(f"❌ Erreur accrual automatique pour {user_obj.username}: {str(e)}")
        
        logger.info(f"📊 Accrual automatique terminé: {updated_count} utilisateurs mis à jour")
        
    except Exception as e:
        logger.error(f"Erreur dans l'accrual automatique à la connexion: {e}")
