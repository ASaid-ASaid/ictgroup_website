"""
Vues du tableau de bord et page d'accueil.
"""

import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

try:
    from ..models import LeaveRequest, TeleworkRequest, UserProfile, get_leave_balance
except ImportError:
    # Fallback pour la compatibilité pendant la migration
    from django.contrib.auth.models import User

    def get_leave_balance(user):
        return {"remaining": 25, "taken": 0, "total": 25}


logger = logging.getLogger(__name__)


@login_required
def home(request):
    """Page d'accueil de l'extranet avec tableau de bord personnalisé."""
    user = request.user

    # Calcul des statistiques pour l'utilisateur
    leave_balance = get_leave_balance(user)

    # Demandes récentes de l'utilisateur
    recent_leaves = LeaveRequest.objects.filter(user=user).order_by("-submitted_at")[:5]
    recent_teleworks = TeleworkRequest.objects.filter(user=user).order_by(
        "-submitted_at"
    )[:5]

    # Demandes en attente de validation (si l'utilisateur a un rôle de validation)
    pending_validations = _get_pending_validations_count(user)

    # Statistiques pour le dashboard
    stats = _get_user_statistics(user)

    context = {
        "user": user,
        "leave_balance": leave_balance,
        "recent_leaves": recent_leaves,
        "recent_teleworks": recent_teleworks,
        "pending_validations": pending_validations,
        "stats": stats,
    }

    return render(request, "extranet/home.html", context)


@login_required
def dashboard_data(request):
    """API pour récupérer les données du dashboard en AJAX."""
    user = request.user

    # Données de base
    data = {
        "leave_balance": get_leave_balance(user),
        "pending_validations": _get_pending_validations_count(user),
        "stats": _get_user_statistics(user),
    }

    # Données spécifiques selon le rôle
    if hasattr(user, "profile"):
        if user.profile.role in ["manager", "rh", "admin"]:
            data["management_stats"] = _get_management_statistics(user)

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

        # Demandes de télétravail où l'utilisateur est manager et validation manager pas encore faite
        count += TeleworkRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).count()

    elif user.profile.role == "rh":
        # Demandes de congé validées par le manager mais pas par RH
        count += LeaveRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).count()

    elif user.profile.role == "admin":
        # Toutes les demandes en attente
        count += LeaveRequest.objects.filter(status="pending").count()
        count += TeleworkRequest.objects.filter(status="pending").count()

    return count


def _get_user_statistics(user):
    """Calcule les statistiques personnelles de l'utilisateur."""
    current_year = date.today().year

    # Congés de l'année
    leaves_this_year = LeaveRequest.objects.filter(
        user=user, start_date__year=current_year, status="approved"
    )

    # Télétravail de l'année
    telework_this_year = TeleworkRequest.objects.filter(
        user=user, start_date__year=current_year, status="approved"
    )

    # Demandes en cours
    pending_leaves = LeaveRequest.objects.filter(user=user, status="pending").count()
    pending_telework = TeleworkRequest.objects.filter(
        user=user, status="pending"
    ).count()

    return {
        "leaves_taken_this_year": leaves_this_year.count(),
        "telework_days_this_year": telework_this_year.count(),
        "pending_leaves": pending_leaves,
        "pending_telework": pending_telework,
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
