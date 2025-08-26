"""
Vues de gestion des demandes de congé.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import LeaveRequestForm
from ..models import LeaveRequest, get_leave_balance
from datetime import date

logger = logging.getLogger(__name__)


@login_required
def leave_request(request):
    """Permet à l'utilisateur de soumettre une nouvelle demande de congé."""
    logger.info(
        "[leave_request] Demande par %s (méthode: %s)",
        request.user.username,
        request.method,
    )

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()

            logger.info(
                "[leave_request] Demande créée pour %s: %s - %s",
                request.user.username,
                leave_request.start_date,
                leave_request.end_date,
            )
            messages.success(
                request, "Votre demande de congé a été soumise avec succès."
            )
            return redirect("extranet:leave_list")
        else:
            logger.warning(
                "[leave_request] Erreurs de validation pour %s: %s",
                request.user.username,
                form.errors,
            )
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = LeaveRequestForm()

    # Calcul du solde de congés
    leave_balance = get_leave_balance(request.user)

    context = {
        "form": form,
        "leave_balance": leave_balance,
    }

    return render(request, "extranet/leave_request.html", context)


@login_required
def leave_list(request):
    """Affiche la liste des demandes de congé de l'utilisateur."""
    user = request.user

    # Traitement de la suppression
    if request.method == "POST" and "delete_leave" in request.POST:
        leave_id = request.POST.get("leave_id")
        if leave_id:
            try:
                leave_to_delete = get_object_or_404(LeaveRequest, id=leave_id, user=user)
                
                # Vérifier si la demande peut être supprimée (seulement en attente ou rejetée)
                if leave_to_delete.status in ["pending", "rejected"]:
                    leave_to_delete.delete()
                    messages.success(request, "Demande de congé supprimée avec succès.")
                    logger.info(f"[leave_list] Demande {leave_id} supprimée par {user.username}")
                else:
                    messages.error(request, "Impossible de supprimer une demande déjà approuvée.")
                    logger.warning(f"[leave_list] Tentative de suppression d'une demande approuvée {leave_id} par {user.username}")
                    
            except Exception as e:
                messages.error(request, "Erreur lors de la suppression de la demande.")
                logger.error(f"[leave_list] Erreur suppression demande {leave_id}: {e}")
                
        return redirect("extranet:leave_list")

    # Récupération des demandes de l'utilisateur avec optimisation
    leaves = LeaveRequest.objects.filter(user=user).select_related('user').order_by("-submitted_at")

    # Filtrage par statut si demandé
    status_filter = request.GET.get("status")
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    # Calcul du solde de congés
    leave_balance = get_leave_balance(user)
    
    # Calcul des congés pris cette année
    today = date.today()
    if today.month >= 6:  # juin à décembre
        period_start = date(today.year, 6, 1)
    else:  # janvier à mai
        period_start = date(today.year - 1, 6, 1)
    
    # Récupérer les demandes approuvées et calculer le total manuellement
    approved_leaves = LeaveRequest.objects.filter(
        user=user,
        status="approved",
        start_date__gte=period_start
    )
    
    leave_taken = 0
    for leave in approved_leaves:
        leave_taken += leave.get_nb_days

    context = {
        "leaves": leaves,
        "leave_balance": leave_balance.get('remaining', 0),
        "leave_taken": leave_balance.get('taken', 0),
        "status_filter": status_filter,
        "status_choices": LeaveRequest.STATUS_CHOICES,
    }

    return render(request, "extranet/leave_list.html", context)


def can_validate_leaves(user):
    """Vérifie si l'utilisateur peut valider des demandes de congé."""
    return hasattr(user, "profile") and user.profile.role in ["manager", "rh", "admin"]


@login_required
@user_passes_test(can_validate_leaves)
def validate_leave(request):
    """Interface de validation des demandes de congé."""
    user = request.user

    # Traitement des actions POST
    if request.method == "POST":
        action = request.POST.get("action")
        leave_id = request.POST.get("leave_id")

        if action and leave_id:
            leave_request = get_object_or_404(LeaveRequest, id=leave_id)

            # Vérification des permissions de validation
            if _can_user_validate_leave(user, leave_request):
                success = _process_leave_validation(user, leave_request, action)
                if success:
                    messages.success(request, f"Demande de congé {action} avec succès.")
                else:
                    messages.error(request, "Erreur lors du traitement de la demande.")
            else:
                messages.error(
                    request,
                    "Vous n'avez pas les permissions pour traiter cette demande.",
                )

            return redirect("extranet:validate_leave")

    # Récupération des demandes à valider
    pending_leaves = _get_leaves_to_validate(user)

    # Déterminer les rôles de validation de l'utilisateur
    can_validate_as_manager = hasattr(user, 'profile') and (
        user.profile.role in ['manager', 'admin'] or 
        # Utilisateur peut être manager d'autres utilisateurs
        any(leave.user.profile.manager == user for leave in pending_leaves)
    )
    
    can_validate_as_rh = hasattr(user, 'profile') and (
        user.profile.role in ['rh', 'admin'] or
        # Utilisateur peut être RH d'autres utilisateurs (même avec rôle manager)
        any(leave.user.profile.rh == user for leave in pending_leaves)
    )

    context = {
        "pending_leaves": pending_leaves,
        "user_role": user.profile.role if hasattr(user, "profile") else None,
        "can_validate_as_manager": can_validate_as_manager,
        "can_validate_as_rh": can_validate_as_rh,
    }

    return render(request, "extranet/validation.html", context)


def _can_user_validate_leave(user, leave_request):
    """Vérifie si l'utilisateur peut valider une demande spécifique."""
    if not hasattr(user, "profile"):
        return False

    role = user.profile.role

    if role == "admin":
        return True

    # Vérifier les capacités de validation indépendamment du rôle principal
    can_validate_as_manager = False
    can_validate_as_rh = False
    
    # Manager peut valider si c'est son équipe et pas encore validé manager
    is_manager_of_user = leave_request.user.profile.manager == user
    if is_manager_of_user and not leave_request.manager_validated:
        can_validate_as_manager = True
        
    # RH peut valider si c'est son secteur, manager validé et pas encore validé RH
    is_rh_of_user = leave_request.user.profile.rh == user
    if is_rh_of_user and leave_request.manager_validated and not leave_request.rh_validated:
        can_validate_as_rh = True
        
    # Retourner True si au moins une capacité de validation existe
    return can_validate_as_manager or can_validate_as_rh


def _process_leave_validation(user, leave_request, action):
    """Traite la validation ou le rejet d'une demande de congé."""
    try:
        role = user.profile.role

        if action == "manager_approve":
            # Validation spécifique manager
            if leave_request.user.profile.manager == user and not leave_request.manager_validated:
                leave_request.manager_validated = True
                leave_request.manager_validated_at = timezone.now()
                leave_request.manager_comment = ""

                # Si pas de RH assigné, approuver directement
                if not leave_request.user.profile.rh:
                    leave_request.status = "approved"

        elif action == "rh_approve":
            # Validation spécifique RH
            if leave_request.user.profile.rh == user and leave_request.manager_validated and not leave_request.rh_validated:
                leave_request.rh_validated = True
                leave_request.rh_validated_at = timezone.now()
                leave_request.status = "approved"

        elif action == "approve":
            # Ancienne logique pour compatibilité (admin principalement)
            if role == "admin":
                leave_request.admin_validated = True
                leave_request.admin_validated_at = timezone.now()
                leave_request.status = "approved"
            elif role == "manager" and leave_request.user.profile.manager == user:
                leave_request.manager_validated = True
                leave_request.manager_validated_at = timezone.now()
                if not leave_request.user.profile.rh:
                    leave_request.status = "approved"
            elif role == "rh" and leave_request.user.profile.rh == user:
                leave_request.rh_validated = True
                leave_request.rh_validated_at = timezone.now()
                leave_request.status = "approved"

        elif action == "reject":
            leave_request.status = "rejected"

            if role == "manager":
                leave_request.manager_comment = "Rejetée par le manager"
            elif role == "rh":
                leave_request.rh_comment = "Rejetée par les RH"

        leave_request.save()

        logger.info(
            f"[validate_leave] Demande {leave_request.id} {action} par {user.username}"
        )
        return True

    except Exception as e:
        logger.error(f"[validate_leave] Erreur lors du traitement: {e}")
        return False


def _get_leaves_to_validate(user):
    """Récupère les demandes de congé que l'utilisateur peut valider."""
    from django.db.models import Q
    
    logger.info(f"[_get_leaves_to_validate] Début - Utilisateur: {user.username}, Role: {user.profile.role}")
    
    # Base query - demandes en attente (non rejetées, non annulées)
    base_queryset = LeaveRequest.objects.filter(
        status__in=['pending', 'approved']
    ).select_related('user__profile')
    
    logger.info(f"[_get_leaves_to_validate] Base queryset count: {base_queryset.count()}")
    
    # Log de toutes les demandes de base
    for leave in base_queryset:
        logger.info(f"[_get_leaves_to_validate] Demande trouvée: ID={leave.id}, User={leave.user.username}, Status={leave.status}, Manager_validated={leave.manager_validated}, RH_validated={leave.rh_validated}, Manager={leave.user.profile.manager}, RH={leave.user.profile.rh}")
    
    # Conditions selon le rôle
    if user.profile.role in ['admin', 'rh']:
        # Admin et RH peuvent voir toutes les demandes
        logger.info(f"[_get_leaves_to_validate] Utilisateur Admin/RH - Toutes les demandes")
        return base_queryset.filter(status='pending')
    elif user.profile.role == 'manager':
        # Manager peut voir les demandes de ses équipes qui ne sont pas encore validées manager
        from ..models import UserProfile
        team_users = UserProfile.objects.filter(manager=user).values_list('user', flat=True)
        logger.info(f"[_get_leaves_to_validate] Manager - Team users: {list(team_users)}")
        
        # Demandes en attente sans validation manager
        manager_queryset = base_queryset.filter(
            user__in=team_users,
            status='pending',
            manager_validated=False
        )
        logger.info(f"[_get_leaves_to_validate] Manager queryset count: {manager_queryset.count()}")
        
        # Ajouter les demandes où l'utilisateur est RH pour certains employés
        rh_users = UserProfile.objects.filter(rh=user).values_list('user', flat=True)
        logger.info(f"[_get_leaves_to_validate] RH users pour {user.username}: {list(rh_users)}")
        
        if rh_users:
            # Pour les demandes où il est RH, ne prendre que celles validées par manager mais pas par RH
            rh_queryset = base_queryset.filter(
                user__in=rh_users,
                status='pending',
                manager_validated=True,
                rh_validated=False
            )
            logger.info(f"[_get_leaves_to_validate] RH queryset count: {rh_queryset.count()}")
            
            # Log des demandes RH spécifiques
            for leave in rh_queryset:
                logger.info(f"[_get_leaves_to_validate] Demande RH: ID={leave.id}, User={leave.user.username}, Status={leave.status}, Manager_validated={leave.manager_validated}, RH_validated={leave.rh_validated}")
            
            # Combiner les deux querysets
            all_leaves = list(manager_queryset) + list(rh_queryset)
            logger.info(f"[_get_leaves_to_validate] Combined count: {len(all_leaves)}")
            
            # Retourner un queryset unique
            leave_ids = [leave.id for leave in all_leaves]
            final_queryset = base_queryset.filter(id__in=leave_ids)
            logger.info(f"[_get_leaves_to_validate] Final queryset count: {final_queryset.count()}")
            return final_queryset
        
        return manager_queryset
    else:
        logger.info(f"[_get_leaves_to_validate] Utilisateur standard - Aucune demande")
        return LeaveRequest.objects.none()
