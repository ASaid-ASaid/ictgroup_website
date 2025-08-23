"""
Vues de gestion des demandes de congé.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import LeaveRequestForm
from ..models import LeaveRequest, UserProfile, get_leave_balance

logger = logging.getLogger(__name__)


@login_required
def leave_request(request):
    """Permet à l'utilisateur de soumettre une nouvelle demande de congé."""
    logger.info(
        f"[leave_request] Demande par {request.user.username} (méthode: {request.method})"
    )

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()

            logger.info(
                f"[leave_request] Demande créée pour {request.user.username}: {leave_request.start_date} - {leave_request.end_date}"
            )
            messages.success(
                request, "Votre demande de congé a été soumise avec succès."
            )
            return redirect("extranet:leave_list")
        else:
            logger.warning(
                f"[leave_request] Erreurs de validation pour {request.user.username}: {form.errors}"
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

    # Récupération des demandes de l'utilisateur
    leaves = LeaveRequest.objects.filter(user=user).order_by("-submitted_at")

    # Filtrage par statut si demandé
    status_filter = request.GET.get("status")
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    # Calcul du solde de congés
    leave_balance = get_leave_balance(user)

    context = {
        "leaves": leaves,
        "leave_balance": leave_balance,
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

    context = {
        "pending_leaves": pending_leaves,
        "user_role": user.profile.role if hasattr(user, "profile") else None,
    }

    return render(request, "extranet/validation.html", context)


def _can_user_validate_leave(user, leave_request):
    """Vérifie si l'utilisateur peut valider une demande spécifique."""
    if not hasattr(user, "profile"):
        return False

    role = user.profile.role

    if role == "admin":
        return True
    elif role == "manager":
        return (
            leave_request.user.profile.manager == user
            and not leave_request.manager_validated
        )
    elif role == "rh":
        return (
            leave_request.user.profile.rh == user
            and leave_request.manager_validated
            and not leave_request.rh_validated
        )

    return False


def _process_leave_validation(user, leave_request, action):
    """Traite la validation ou le rejet d'une demande de congé."""
    try:
        role = user.profile.role

        if action == "approve":
            if role == "manager":
                leave_request.manager_validated = True
                leave_request.manager_validated_at = timezone.now()
                leave_request.manager_comment = ""

                # Si pas de RH assigné, approuver directement
                if not leave_request.user.profile.rh:
                    leave_request.status = "approved"

            elif role == "rh":
                leave_request.rh_validated = True
                leave_request.rh_validated_at = timezone.now()
                leave_request.status = "approved"

            elif role == "admin":
                leave_request.admin_validated = True
                leave_request.admin_validated_at = timezone.now()
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
    if not hasattr(user, "profile"):
        return LeaveRequest.objects.none()

    role = user.profile.role

    if role == "admin":
        return LeaveRequest.objects.filter(status="pending").order_by("-submitted_at")
    elif role == "manager":
        return LeaveRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).order_by("-submitted_at")
    elif role == "rh":
        return LeaveRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).order_by("-submitted_at")

    return LeaveRequest.objects.none()
