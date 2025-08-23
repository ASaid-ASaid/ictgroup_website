"""
Gestionnaires optimisés pour les calculs de congés et rapports mensuels.
Utilise les tables de cache pour éviter les recalculs répétitifs.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from workalendar.europe import France
import logging

logger = logging.getLogger(__name__)


class OptimizedLeaveManager:
    """
    Gestionnaire optimisé pour les calculs de soldes de congés.
    Utilise la table UserLeaveBalanceCache pour éviter les recalculs.
    """
    
    @staticmethod
    def get_or_calculate_balance(user, year=None):
        """
        Récupère ou calcule le solde de congés pour un utilisateur.
        Utilise le cache si disponible et à jour, sinon recalcule.
        """
        if year is None:
            year = date.today().year
            
        from .models import UserLeaveBalanceCache, LeaveRequest
        
        # Essayer de récupérer depuis le cache
        try:
            cache_entry = UserLeaveBalanceCache.objects.get(user=user, year=year)
            # Vérifier si le cache est récent (moins de 1 heure)
            if (timezone.now() - cache_entry.last_updated).total_seconds() < 3600:
                return {
                    'acquired': float(cache_entry.acquired_days),
                    'taken': float(cache_entry.taken_days),
                    'carry_over': float(cache_entry.carry_over_days),
                    'balance': float(cache_entry.remaining_days),
                    'from_cache': True
                }
        except UserLeaveBalanceCache.DoesNotExist:
            cache_entry = None
        
        # Recalculer si pas de cache ou cache obsolète
        balance = OptimizedLeaveManager._calculate_balance(user, year)
        
        # Mettre à jour ou créer le cache
        if cache_entry:
            cache_entry.acquired_days = Decimal(str(balance['acquired']))
            cache_entry.taken_days = Decimal(str(balance['taken']))
            cache_entry.carry_over_days = Decimal(str(balance['carry_over']))
            cache_entry.remaining_days = Decimal(str(balance['balance']))
            cache_entry.save()
        else:
            UserLeaveBalanceCache.objects.create(
                user=user,
                year=year,
                acquired_days=Decimal(str(balance['acquired'])),
                taken_days=Decimal(str(balance['taken'])),
                carry_over_days=Decimal(str(balance['carry_over'])),
                remaining_days=Decimal(str(balance['balance']))
            )
        
        balance['from_cache'] = False
        return balance
    
    @staticmethod
    def _calculate_balance(user, year):
        """
        Calcule le solde de congés pour un utilisateur sur une année.
        """
        from .models import LeaveRequest
        
        # Jours acquis par défaut (peut être configuré selon les règles métier)
        acquired_days = 25.0  # 25 jours par an standard
        
        # Report de l'année précédente
        carry_over = 0.0
        if hasattr(user, 'profile') and user.profile.carry_over:
            carry_over = float(user.profile.carry_over)
        
        # Congés pris dans l'année
        taken_leaves = LeaveRequest.objects.filter(
            user=user,
            status='approved',
            start_date__year=year
        )
        
        taken_days = 0.0
        for leave in taken_leaves:
            if leave.demi_jour in ['am', 'pm']:
                taken_days += 0.5
            else:
                taken_days += (leave.end_date - leave.start_date).days + 1
        
        # Calcul du solde restant
        balance = acquired_days + carry_over - taken_days
        
        return {
            'acquired': acquired_days,
            'taken': taken_days,
            'carry_over': carry_over,
            'balance': balance
        }
    
    @staticmethod
    def invalidate_cache(user, year=None):
        """
        Invalide le cache de solde pour un utilisateur.
        À appeler quand une demande de congé est modifiée.
        """
        from .models import UserLeaveBalanceCache
        
        if year:
            UserLeaveBalanceCache.objects.filter(user=user, year=year).delete()
        else:
            UserLeaveBalanceCache.objects.filter(user=user).delete()


class OptimizedMonthlyReportManager:
    """
    Gestionnaire optimisé pour les rapports mensuels.
    Utilise la table UserMonthlyReportCache pour éviter les recalculs.
    """
    
    @staticmethod
    def get_or_calculate_monthly_data(user, year, month):
        """
        Récupère ou calcule les données mensuelles pour un utilisateur.
        """
        from .models import UserMonthlyReportCache
        
        # Essayer de récupérer depuis le cache
        try:
            cache_entry = UserMonthlyReportCache.objects.get(
                user=user, year=year, month=month
            )
            # Vérifier si le cache est récent (moins de 1 heure)
            if (timezone.now() - cache_entry.last_updated).total_seconds() < 3600:
                return {
                    'days_at_office': cache_entry.days_at_office,
                    'days_telework': cache_entry.days_telework,
                    'days_leave': float(cache_entry.days_leave),
                    'total_workdays': cache_entry.total_workdays,
                    'from_cache': True
                }
        except UserMonthlyReportCache.DoesNotExist:
            cache_entry = None
        
        # Recalculer si pas de cache ou cache obsolète
        data = OptimizedMonthlyReportManager._calculate_monthly_data(user, year, month)
        
        # Mettre à jour ou créer le cache
        if cache_entry:
            cache_entry.days_at_office = data['days_at_office']
            cache_entry.days_telework = data['days_telework']
            cache_entry.days_leave = Decimal(str(data['days_leave']))
            cache_entry.total_workdays = data['total_workdays']
            cache_entry.save()
        else:
            UserMonthlyReportCache.objects.create(
                user=user,
                year=year,
                month=month,
                days_at_office=data['days_at_office'],
                days_telework=data['days_telework'],
                days_leave=Decimal(str(data['days_leave'])),
                total_workdays=data['total_workdays']
            )
        
        data['from_cache'] = False
        return data
    
    @staticmethod
    def _calculate_monthly_data(user, year, month):
        """
        Calcule les données mensuelles pour un utilisateur.
        """
        from .models import LeaveRequest, TeleworkRequest
        
        # Calcul des dates du mois
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Calcul total jours ouvrés
        cal_fr = France()
        holidays = set(dt for dt, _ in cal_fr.holidays(year))
        
        total_workdays = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5 and current_date not in holidays:
                total_workdays += 1
            current_date += timedelta(days=1)
        
        # Calcul jours de congés pris
        user_leaves = LeaveRequest.objects.filter(
            user=user,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        days_leave = 0.0
        for leave in user_leaves:
            if leave.demi_jour in ['am', 'pm'] and leave.start_date == leave.end_date:
                # Demi-journée
                if start_date <= leave.start_date <= end_date:
                    days_leave += 0.5
            else:
                # Congé complet - compter jours ouvrés uniquement
                leave_start = max(leave.start_date, start_date)
                leave_end = min(leave.end_date, end_date)
                
                current_date = leave_start
                while current_date <= leave_end:
                    if current_date.weekday() < 5 and current_date not in holidays:
                        days_leave += 1
                    current_date += timedelta(days=1)
        
        # Calcul jours de télétravail (jours ouvrés uniquement)
        user_teleworks = TeleworkRequest.objects.filter(
            user=user,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        days_telework = 0
        for telework in user_teleworks:
            tw_start = max(telework.start_date, start_date)
            tw_end = min(telework.end_date, end_date)
            
            current_date = tw_start
            while current_date <= tw_end:
                if current_date.weekday() < 5 and current_date not in holidays:
                    days_telework += 1
                current_date += timedelta(days=1)
        
        # Calcul jours au bureau
        days_at_office = max(0, total_workdays - int(days_leave) - days_telework)
        
        return {
            'days_at_office': days_at_office,
            'days_telework': days_telework,
            'days_leave': days_leave,
            'total_workdays': total_workdays
        }
    
    @staticmethod
    def invalidate_cache(user, year=None, month=None):
        """
        Invalide le cache de rapport mensuel pour un utilisateur.
        """
        from .models import UserMonthlyReportCache
        
        queryset = UserMonthlyReportCache.objects.filter(user=user)
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)
        
        queryset.delete()
    
    @staticmethod
    def get_bulk_monthly_data(users, year, month):
        """
        Récupère les données mensuelles pour plusieurs utilisateurs en bulk.
        Optimise les requêtes pour les rapports globaux.
        """
        results = {}
        for user in users:
            results[user.id] = OptimizedMonthlyReportManager.get_or_calculate_monthly_data(
                user, year, month
            )
        return results
