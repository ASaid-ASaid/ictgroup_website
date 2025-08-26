"""
Vues du tableau de bord et page d'accueil.
Version optimisée avec cache et requêtes efficaces.
"""

import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache import cache

try:
    from ..models import LeaveRequest, TeleworkRequest, OverTimeRequest, UserProfile, get_leave_balance, Document
    from ..utils import (
        get_cached_leave_balance, 
        get_cached_user_statistics, 
        get_optimized_recent_requests,
        get_optimized_pending_validations
    )
except ImportError:
    # Fallback minimal pour la compatibilité pendant la migration
    def get_leave_balance(user):
        return {"remaining": 25, "taken": 0, "total": 25}
    
    def get_cached_leave_balance(user):
        return get_leave_balance(user)
    
    def get_cached_user_statistics(user):
        return {}
    
    def get_optimized_recent_requests(user):
        return {'leaves': [], 'teleworks': [], 'overtimes': []}
    
    def get_optimized_pending_validations(user):
        return 0


logger = logging.getLogger(__name__)


@login_required
def home(request):
    """Page d'accueil de l'extranet avec tableau de bord personnalisé optimisé."""
    user = request.user

    # Utiliser les fonctions cachées pour de meilleures performances
    leave_balance = get_cached_leave_balance(user)
    
    # Demandes récentes optimisées
    recent_requests = get_optimized_recent_requests(user)
    recent_leaves = recent_requests['leaves']
    recent_teleworks = recent_requests['teleworks'] 
    recent_overtimes = recent_requests['overtimes']

    # Demandes en attente de validation (optimisées)
    pending_validations = get_optimized_pending_validations(user)

    # Documents récents accessibles à l'utilisateur (avec cache)
    cache_key = f"recent_documents_{user.id}"
    recent_documents = cache.get(cache_key)
    
    if recent_documents is None:
        try:
            recent_documents = []
            all_documents = Document.objects.filter(is_active=True).select_related('uploaded_by').order_by("-uploaded_at")[:10]
            for doc in all_documents:
                if doc.can_user_access(user):
                    recent_documents.append(doc)
                    if len(recent_documents) >= 5:  # Limiter à 5 documents
                        break
            # Cache pour 10 minutes
            cache.set(cache_key, recent_documents, 600)
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des documents récents: {e}")
            recent_documents = []

    # Statistiques optimisées
    stats = get_cached_user_statistics(user)

    context = {
        "user": user,
        "leave_balance": leave_balance,
        "recent_leaves": recent_leaves,
        "recent_teleworks": recent_teleworks,
        "recent_overtimes": recent_overtimes,
        "recent_documents": recent_documents,
        "pending_validations": pending_validations,
        "stats": stats,
    }

    return render(request, "extranet/home.html", context)


@login_required
@cache_page(300)  # Cache pendant 5 minutes
def dashboard_data(request):
    """API pour récupérer les données du dashboard en AJAX (version optimisée)."""
    user = request.user

    # Cache key spécifique à l'utilisateur
    cache_key = f"dashboard_data_{user.id}"
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return JsonResponse(cached_data)

    # Données de base optimisées
    data = {
        "leave_balance": get_cached_leave_balance(user),
        "pending_validations": get_optimized_pending_validations(user),
        "stats": get_cached_user_statistics(user),
    }

    # Données spécifiques selon le rôle
    if hasattr(user, "profile"):
        if user.profile.role in ["manager", "rh", "admin"]:
            data["management_stats"] = _get_management_statistics(user)

    # Cache pour 5 minutes
    cache.set(cache_key, data, 300)
    
    return JsonResponse(data)


def _get_pending_validations_count(user):
    """Calcule le nombre de demandes en attente de validation pour l'utilisateur."""
    if not hasattr(user, "profile") or user.profile.role not in [
        "manager",
        "rh",
        "admin",
    ]:
        return 0

    count = 0

    if user.profile.role == "manager":
        # Demandes de congé où l'utilisateur est manager et validation manager pas encore faite
        count += LeaveRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).count()

        # Demandes de télétravail où l'utilisateur est manager
        # et validation manager pas encore faite
        count += TeleworkRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).count()
        
        # Heures supplémentaires où l'utilisateur est manager
        try:
            count += OverTimeRequest.objects.filter(
                status="pending", user__profile__manager=user, manager_validated=False
            ).count()
        except Exception:
            pass

    elif user.profile.role == "rh":
        # Demandes de congé validées par le manager mais pas par RH
        count += LeaveRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).count()
        
        # Heures supplémentaires validées par le manager mais pas par RH
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
        # Toutes les demandes en attente
        count += LeaveRequest.objects.filter(status="pending").count()
        count += TeleworkRequest.objects.filter(status="pending").count()
        try:
            count += OverTimeRequest.objects.filter(status="pending").count()
        except Exception:
            pass

    return count


def _get_user_statistics(user):
    """Calcule les statistiques personnelles de l'utilisateur."""
    current_year = date.today().year

    # Utiliser select_related pour optimiser les requêtes
    # Congés de l'année
    leaves_this_year = LeaveRequest.objects.filter(
        user=user, start_date__year=current_year, status="approved"
    ).select_related('user')

    # Télétravail de l'année  
    telework_this_year = TeleworkRequest.objects.filter(
        user=user, start_date__year=current_year, status="approved"
    ).select_related('user')
    
    # Heures supplémentaires de l'année
    try:
        overtime_this_year = OverTimeRequest.objects.filter(
            user=user, work_date__year=current_year, status="approved"
        ).select_related('user')
        total_overtime_hours = sum(overtime.hours for overtime in overtime_this_year)
        
        # Heures supplémentaires du mois en cours
        current_month_start = date.today().replace(day=1)
        if current_month_start.month == 12:
            next_month_start = current_month_start.replace(year=current_month_start.year + 1, month=1)
        else:
            next_month_start = current_month_start.replace(month=current_month_start.month + 1)
        
        overtime_this_month = OverTimeRequest.objects.filter(
            user=user, 
            work_date__gte=current_month_start,
            work_date__lt=next_month_start,
            status="approved"
        ).select_related('user')
        total_overtime_hours_month = sum(overtime.hours for overtime in overtime_this_month)
    except Exception as e:
        logger.warning(f"Erreur lors du calcul des heures supplémentaires: {e}")
        total_overtime_hours = 0
        total_overtime_hours_month = 0

    # Utiliser count() au lieu de charger tous les objets
    pending_leaves = LeaveRequest.objects.filter(user=user, status="pending").count()
    pending_telework = TeleworkRequest.objects.filter(
        user=user, status="pending"
    ).count()
    
    try:
        pending_overtime = OverTimeRequest.objects.filter(user=user, status="pending").count()
    except Exception:
        pending_overtime = 0

    return {
        "leaves_taken_this_year": leaves_this_year.count(),
        "telework_days_this_year": telework_this_year.count(),
        "overtime_hours_this_year": total_overtime_hours,
        "overtime_hours_this_month": total_overtime_hours_month,
        "pending_leaves": pending_leaves,
        "pending_telework": pending_telework,
        "pending_overtime": pending_overtime,
        "total_requests_this_year": leaves_this_year.count()
        + telework_this_year.count(),
    }


def _get_management_statistics(user):
    """Calcule les statistiques de gestion pour les managers/RH/admins."""
    if not hasattr(user, "profile") or user.profile.role not in [
        "manager",
        "rh",
        "admin",
    ]:
        return {}

    current_month = date.today().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)

    stats = {}

    if user.profile.role == "manager":
        # Équipe du manager
        team_members = UserProfile.objects.filter(manager=user).count()

        # Demandes de l'équipe ce mois
        team_leaves_this_month = LeaveRequest.objects.filter(
            user__profile__manager=user,
            start_date__gte=current_month,
            start_date__lt=next_month,
        ).count()

        stats.update(
            {
                "team_size": team_members,
                "team_leaves_this_month": team_leaves_this_month,
            }
        )

    elif user.profile.role in ["rh", "admin"]:
        # Statistiques globales
        total_users = UserProfile.objects.count()

        # Demandes ce mois
        leaves_this_month = LeaveRequest.objects.filter(
            start_date__gte=current_month, start_date__lt=next_month
        ).count()

        telework_this_month = TeleworkRequest.objects.filter(
            start_date__gte=current_month, start_date__lt=next_month
        ).count()

        stats.update(
            {
                "total_users": total_users,
                "leaves_this_month": leaves_this_month,
                "telework_this_month": telework_this_month,
            }
        )

    return stats
