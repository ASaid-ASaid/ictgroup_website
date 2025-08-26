"""
Utilitaires pour l'optimisation des performances de l'extranet.
Fonctions de cache, optimisations de requêtes, etc.
"""

import logging
from functools import wraps
from datetime import date, timedelta
from django.core.cache import cache
from django.db.models import Q, Prefetch
from django.conf import settings

logger = logging.getLogger('extranet')
perf_logger = logging.getLogger('performance')


def cache_user_data(timeout=300):
    """
    Décorateur pour mettre en cache les données utilisateur.
    Args:
        timeout: Durée du cache en secondes (défaut: 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            # Clé de cache unique par utilisateur et fonction
            cache_key = f"user_data_{user.id}_{func.__name__}_{hash(str(args))}"
            
            # Vérifier le cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                perf_logger.info(f"Cache HIT: {cache_key}")
                return cached_result
            
            # Calculer et mettre en cache
            result = func(user, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            perf_logger.info(f"Cache SET: {cache_key}")
            
            return result
        return wrapper
    return decorator


def invalidate_user_cache(user):
    """Invalide tout le cache lié à un utilisateur"""
    cache_patterns = [
        f"user_data_{user.id}_*",
        f"leave_balance_{user.id}_*",
        f"user_stats_{user.id}_*",
    ]
    
    for pattern in cache_patterns:
        # Note: Tentative de delete_pattern avec fallback
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
                perf_logger.info(f"Cache invalidated: {pattern}")
            else:
                # Fallback : supprimer les clés une par une (moins efficace)
                for key in [f"user_data_{user.id}_get_cached_leave_balance", 
                           f"user_data_{user.id}_get_cached_user_statistics",
                           f"recent_requests_{user.id}_5",
                           f"pending_validations_{user.id}",
                           f"recent_documents_{user.id}"]:
                    cache.delete(key)
                perf_logger.info(f"Cache invalidated (fallback): {user.id}")
        except Exception as e:
            logger.warning(f"Cache invalidation error for {pattern}: {e}")


@cache_user_data(timeout=600)  # 10 minutes
def get_cached_leave_balance(user):
    """Version cachée de get_leave_balance"""
    from .models import get_leave_balance
    return get_leave_balance(user)


@cache_user_data(timeout=300)  # 5 minutes  
def get_cached_user_statistics(user):
    """Version cachée des statistiques utilisateur"""
    from .models import LeaveRequest, TeleworkRequest, OverTimeRequest
    
    current_year = date.today().year
    
    # Utiliser select_related pour optimiser
    leaves_this_year = LeaveRequest.objects.filter(
        user=user, start_date__year=current_year, status="approved"
    ).select_related('user')
    
    telework_this_year = TeleworkRequest.objects.filter(
        user=user, start_date__year=current_year, status="approved"
    ).select_related('user')
    
    try:
        overtime_this_year = OverTimeRequest.objects.filter(
            user=user, work_date__year=current_year, status="approved"
        ).select_related('user')
        total_overtime_hours = sum(overtime.hours for overtime in overtime_this_year)
    except Exception:
        total_overtime_hours = 0
    
    return {
        "leaves_taken_this_year": leaves_this_year.count(),
        "telework_days_this_year": telework_this_year.count(),
        "overtime_hours_this_year": total_overtime_hours,
        "pending_leaves": LeaveRequest.objects.filter(user=user, status="pending").count(),
        "pending_telework": TeleworkRequest.objects.filter(user=user, status="pending").count(),
    }


def optimize_queryset_for_user_list(queryset, user_field='user'):
    """
    Optimise un queryset pour éviter les requêtes N+1 lors de l'affichage de listes.
    
    Args:
        queryset: Le queryset à optimiser
        user_field: Le nom du champ utilisateur (défaut: 'user')
    """
    return queryset.select_related(
        f'{user_field}',
        f'{user_field}__profile'
    ).prefetch_related(
        f'{user_field}__leave_requests',
        f'{user_field}__telework_requests'
    )


def get_optimized_recent_requests(user, limit=5):
    """
    Récupère les demandes récentes de l'utilisateur de manière optimisée.
    
    Args:
        user: L'utilisateur
        limit: Nombre de demandes à récupérer
    """
    from .models import LeaveRequest, TeleworkRequest, OverTimeRequest
    
    # Cache key
    cache_key = f"recent_requests_{user.id}_{limit}"
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return cached_result
    
    # Requêtes optimisées
    recent_leaves = list(LeaveRequest.objects.filter(user=user)
                        .select_related('user')
                        .order_by("-submitted_at")[:limit])
    
    recent_teleworks = list(TeleworkRequest.objects.filter(user=user)
                           .select_related('user')
                           .order_by("-submitted_at")[:limit])
    
    try:
        recent_overtimes = list(OverTimeRequest.objects.filter(user=user)
                               .select_related('user')
                               .order_by("-submitted_at")[:limit])
    except Exception:
        recent_overtimes = []
    
    result = {
        'leaves': recent_leaves,
        'teleworks': recent_teleworks,
        'overtimes': recent_overtimes
    }
    
    # Cache pour 5 minutes
    cache.set(cache_key, result, 300)
    
    return result


def get_optimized_pending_validations(user):
    """
    Calcule le nombre de demandes en attente de validation de manière optimisée.
    """
    from .models import LeaveRequest, TeleworkRequest, OverTimeRequest
    
    cache_key = f"pending_validations_{user.id}"
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return cached_result
    
    count = 0
    
    if not hasattr(user, "profile") or user.profile.role not in ["manager", "rh", "admin"]:
        cache.set(cache_key, 0, 300)
        return 0
    
    if user.profile.role == "manager":
        count += LeaveRequest.objects.filter(
            status="pending", 
            user__profile__manager=user, 
            manager_validated=False
        ).count()
        
        count += TeleworkRequest.objects.filter(
            status="pending", 
            user__profile__manager=user, 
            manager_validated=False
        ).count()
        
        try:
            count += OverTimeRequest.objects.filter(
                status="pending", 
                user__profile__manager=user, 
                manager_validated=False
            ).count()
        except Exception:
            pass
    
    elif user.profile.role == "rh":
        count += LeaveRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).count()
        
        try:
            count += OverTimeRequest.objects.filter(
                status="pending",
                user__profile__rh=user,
                manager_validated=True,
                rh_validated=False,
            ).count()
        except Exception:
            pass
    
    elif user.profile.role == "admin":
        count += LeaveRequest.objects.filter(status="pending").count()
        count += TeleworkRequest.objects.filter(status="pending").count()
        try:
            count += OverTimeRequest.objects.filter(status="pending").count()
        except Exception:
            pass
    
    # Cache pour 2 minutes (données sensibles aux changements)
    cache.set(cache_key, count, 120)
    
    return count


class PerformanceMiddleware:
    """
    Middleware pour tracer les performances des vues.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        # Log les vues lentes (> 500ms)
        if duration > 0.5:
            perf_logger.warning(
                f"Slow view: {request.path} took {duration:.2f}s "
                f"(User: {getattr(request.user, 'username', 'Anonymous')})"
            )
        
        # Ajouter header de performance
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


def batch_update_user_stats(users, year=None, month=None):
    """
    Met à jour les statistiques de plusieurs utilisateurs en lot.
    Plus efficace que les mises à jour individuelles.
    """
    from .models import MonthlyUserStats
    
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month
    
    stats_to_update = []
    
    for user in users:
        stats, created = MonthlyUserStats.objects.get_or_create(
            user=user,
            year=year,
            month=month
        )
        stats_to_update.append(stats)
    
    # Mise à jour en lot
    for stats in stats_to_update:
        stats.update_from_requests()
    
    perf_logger.info(f"Batch updated {len(stats_to_update)} user stats for {year}-{month}")


def warm_up_cache():
    """
    Précalcule les données critiques dans le cache.
    À exécuter après un redémarrage ou une invalidation du cache.
    """
    from django.contrib.auth.models import User
    from .models import get_leave_balance
    
    active_users = User.objects.filter(is_active=True).select_related('profile')
    
    perf_logger.info(f"Warming up cache for {active_users.count()} users")
    
    for user in active_users:
        try:
            # Précalculer les soldes de congés
            get_cached_leave_balance(user)
            
            # Précalculer les statistiques
            get_cached_user_statistics(user)
            
            # Précalculer les demandes récentes
            get_optimized_recent_requests(user)
            
            # Précalculer les validations en attente
            get_optimized_pending_validations(user)
            
        except Exception as e:
            logger.error(f"Error warming cache for user {user.username}: {e}")
    
    perf_logger.info("Cache warm-up completed")


def clear_expired_cache():
    """
    Nettoie le cache des entrées expirées.
    À exécuter périodiquement via une tâche cron.
    """
    try:
        # Clear all expired keys
        cache.clear()
        perf_logger.info("Cache cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
