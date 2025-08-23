"""
Vues de gestion des demandes de télétravail.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import TeleworkRequestForm
from ..models import TeleworkRequest, UserProfile

logger = logging.getLogger(__name__)


@login_required
def telework_request(request):
    """Permet à l'utilisateur de soumettre une nouvelle demande de télétravail."""
    logger.info(
        f"[telework_request] Demande par {request.user.username} (méthode: {request.method})"
    )

    if request.method == "POST":
        form = TeleworkRequestForm(request.POST)
        if form.is_valid():
            telework_request = form.save(commit=False)
            telework_request.user = request.user
            telework_request.save()

            logger.info(
                f"[telework_request] Demande créée pour {request.user.username}: {telework_request.start_date} - {telework_request.end_date}"
            )
            messages.success(
                request, "Votre demande de télétravail a été soumise avec succès."
            )
            return redirect("extranet:telework_list")
        else:
            logger.warning(
                f"[telework_request] Erreurs de validation pour {request.user.username}: {form.errors}"
            )
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = TeleworkRequestForm()

    context = {
        "form": form,
    }

    return render(request, "extranet/telework_request.html", context)


@login_required
def telework_list(request):
    """Affiche la liste des demandes de télétravail de l'utilisateur."""
    user = request.user

    # Récupération des demandes de l'utilisateur
    teleworks = TeleworkRequest.objects.filter(user=user).order_by("-submitted_at")

    # Filtrage par statut si demandé
    status_filter = request.GET.get("status")
    if status_filter:
        teleworks = teleworks.filter(status=status_filter)

    context = {
        "teleworks": teleworks,
        "status_filter": status_filter,
        "status_choices": TeleworkRequest.STATUS_CHOICES,
    }

    return render(request, "extranet/telework_list.html", context)


def can_validate_telework(user):
    """Vérifie si l'utilisateur peut valider des demandes de télétravail."""
    return hasattr(user, "profile") and user.profile.role in ["manager", "rh", "admin"]


@login_required
@user_passes_test(can_validate_telework)
def validate_telework(request):
    """Interface de validation des demandes de télétravail."""
    user = request.user

    # Traitement des actions POST
    if request.method == "POST":
        action = request.POST.get("action")
        telework_id = request.POST.get("telework_id")

        if action and telework_id:
            telework_request = get_object_or_404(TeleworkRequest, id=telework_id)

            # Vérification des permissions de validation
            if _can_user_validate_telework(user, telework_request):
                success = _process_telework_validation(user, telework_request, action)
                if success:
                    messages.success(
                        request, f"Demande de télétravail {action} avec succès."
                    )
                else:
                    messages.error(request, "Erreur lors du traitement de la demande.")
            else:
                messages.error(
                    request,
                    "Vous n'avez pas les permissions pour traiter cette demande.",
                )

            return redirect("extranet:validate_telework")

    # Récupération des demandes à valider
    pending_teleworks = _get_teleworks_to_validate(user)

    context = {
        "pending_teleworks": pending_teleworks,
        "user_role": user.profile.role if hasattr(user, "profile") else None,
    }

    return render(request, "extranet/telework_validation.html", context)


def _can_user_validate_telework(user, telework_request):
    """Vérifie si l'utilisateur peut valider une demande spécifique."""
    if not hasattr(user, "profile"):
        return False

    role = user.profile.role

    if role == "admin":
        return True
    elif role == "manager":
        return (
            telework_request.user.profile.manager == user
            and not telework_request.manager_validated
        )
    elif role == "rh":
        return (
            telework_request.user.profile.rh == user
            and telework_request.manager_validated
            and not telework_request.rh_validated
        )

    return False


def _process_telework_validation(user, telework_request, action):
    """Traite la validation ou le rejet d'une demande de télétravail."""
    try:
        role = user.profile.role

        if action == "approve":
            if role == "manager":
                telework_request.manager_validated = True
                telework_request.manager_validated_at = timezone.now()
                telework_request.manager_comment = ""

                # Si pas de RH assigné, approuver directement
                if not telework_request.user.profile.rh:
                    telework_request.status = "approved"

            elif role == "rh":
                telework_request.rh_validated = True
                telework_request.rh_validated_at = timezone.now()
                telework_request.status = "approved"

            elif role == "admin":
                telework_request.admin_validated = True
                telework_request.admin_validated_at = timezone.now()
                telework_request.status = "approved"

        elif action == "reject":
            telework_request.status = "rejected"

            if role == "manager":
                telework_request.manager_comment = "Rejetée par le manager"
            elif role == "rh":
                telework_request.rh_comment = "Rejetée par les RH"

        telework_request.save()

        logger.info(
            f"[validate_telework] Demande {telework_request.id} {action} par {user.username}"
        )
        return True

    except Exception as e:
        logger.error(f"[validate_telework] Erreur lors du traitement: {e}")
        return False


def _get_teleworks_to_validate(user):
    """Récupère les demandes de télétravail que l'utilisateur peut valider."""
    if not hasattr(user, "profile"):
        return TeleworkRequest.objects.none()

    role = user.profile.role

    if role == "admin":
        return TeleworkRequest.objects.filter(status="pending").order_by(
            "-submitted_at"
        )
    elif role == "manager":
        return TeleworkRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).order_by("-submitted_at")
    elif role == "rh":
        return TeleworkRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).order_by("-submitted_at")

    return TeleworkRequest.objects.none()


@login_required
def telework_validation(request):
    """Vue pour la validation des demandes de télétravail par les managers et RH."""
    user = request.user

    # Affiche les demandes à valider selon le rôle
    if hasattr(user, "profile") and user.profile.role in [
        "manager",
        "rh",
        "admin",
    ]:
        # Manager : demandes de ses subordonnés + ses propres TT, RH : tous sauf les siens, Admin : tous
        if user.profile.role == "manager":
            telework_requests = TeleworkRequest.objects.filter(
                Q(user__profile__manager=user) | Q(user=user), status="pending"
            )
        elif user.profile.role == "rh":
            telework_requests = TeleworkRequest.objects.filter(
                status="pending"
            ).exclude(user=user)
        else:  # admin
            telework_requests = TeleworkRequest.objects.filter(status="pending")
    else:
        telework_requests = TeleworkRequest.objects.none()

    if request.method == "POST":
        req_id = request.POST.get("request_id")
        action = request.POST.get("action")
        tw = TeleworkRequest.objects.get(id=req_id)
        if action == "approve":
            tw.status = "approved"
            tw.manager_validated = True
            tw.save()
            messages.success(request, "Demande approuvée.")
        elif action == "reject":
            tw.status = "rejected"
            tw.save()
            messages.error(request, "Demande rejetée.")
        return redirect("extranet:telework_validation")

    return render(
        request,
        "extranet/telework_validation.html",
        {"telework_requests": telework_requests},
    )
