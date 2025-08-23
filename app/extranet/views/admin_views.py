"""
Vues d'administration pour la gestion des utilisateurs et rapports.
"""

import csv
import logging
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import UserCreationForm, UserProfileForm
from ..models import LeaveRequest, TeleworkRequest, UserProfile, get_leave_balance

logger = logging.getLogger(__name__)


def is_admin_or_rh(user):
    """Vérifie si l'utilisateur est admin ou RH."""
    return hasattr(user, "profile") and user.profile.role in ["admin", "rh"]


@login_required
@user_passes_test(is_admin_or_rh)
def user_admin(request):
    """Interface d'administration des utilisateurs."""

    # Traitement des actions POST
    if request.method == "POST":
        action = request.POST.get("action", "")

        if "add_user" in request.POST:
            success = _handle_user_creation(request)
        elif "update_user" in request.POST:
            success = _handle_user_update(request)
        elif "delete_user" in request.POST:
            success = _handle_user_deletion(request)
        else:
            messages.error(request, "Action non reconnue.")

        if success:
            return redirect("extranet:user_admin")

    # Export CSV si demandé
    if request.GET.get("export") == "csv":
        return _export_users_csv()

    # Récupération des utilisateurs
    users = User.objects.select_related("profile").all().order_by("username")

    # Calcul des soldes pour chaque utilisateur
    user_balances = {}
    for user in users:
        user_balances[user.id] = get_leave_balance(user)

    context = {
        "users": users,
        "user_balances": user_balances,
        "creation_form": UserCreationForm(),
    }

    return render(request, "extranet/user_admin.html", context)


@login_required
@user_passes_test(is_admin_or_rh)
def admin_leaves(request):
    """Interface d'administration des congés."""

    # Traitement des actions POST
    if request.method == "POST":
        _handle_leave_admin_action(request)
        return redirect("extranet:admin_leaves")

    # Récupération des demandes avec filtres
    leaves = LeaveRequest.objects.select_related("user", "user__profile").all()

    # Filtres
    status_filter = request.GET.get("status")
    user_filter = request.GET.get("user")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if user_filter:
        leaves = leaves.filter(user__username__icontains=user_filter)
    if date_from:
        leaves = leaves.filter(start_date__gte=date_from)
    if date_to:
        leaves = leaves.filter(end_date__lte=date_to)

    leaves = leaves.order_by("-submitted_at")

    # Statistiques
    stats = _calculate_leave_stats(leaves)

    context = {
        "leaves": leaves,
        "stats": stats,
        "status_choices": LeaveRequest.STATUS_CHOICES,
        "filters": {
            "status": status_filter,
            "user": user_filter,
            "date_from": date_from,
            "date_to": date_to,
        },
    }

    return render(request, "extranet/admin_leaves.html", context)


@login_required
@user_passes_test(is_admin_or_rh)
def admin_teleworks(request):
    """Interface d'administration du télétravail."""

    # Traitement des actions POST
    if request.method == "POST":
        _handle_telework_admin_action(request)
        return redirect("extranet:admin_teleworks")

    # Récupération des demandes avec filtres
    teleworks = TeleworkRequest.objects.select_related("user", "user__profile").all()

    # Filtres
    status_filter = request.GET.get("status")
    user_filter = request.GET.get("user")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if status_filter:
        teleworks = teleworks.filter(status=status_filter)
    if user_filter:
        teleworks = teleworks.filter(user__username__icontains=user_filter)
    if date_from:
        teleworks = teleworks.filter(start_date__gte=date_from)
    if date_to:
        teleworks = teleworks.filter(end_date__lte=date_to)

    teleworks = teleworks.order_by("-submitted_at")

    # Statistiques
    stats = _calculate_telework_stats(teleworks)

    context = {
        "teleworks": teleworks,
        "stats": stats,
        "status_choices": TeleworkRequest.STATUS_CHOICES,
        "filters": {
            "status": status_filter,
            "user": user_filter,
            "date_from": date_from,
            "date_to": date_to,
        },
    }

    return render(request, "extranet/admin_teleworks.html", context)


@login_required
@user_passes_test(is_admin_or_rh)
def admin_monthly_report(request):
    """Rapport mensuel pour les RH/Admin - Version optimisée avec cache."""

    # Paramètres de période
    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))

    # Calcul des dates
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    # Import du gestionnaire optimisé
    from ..cache_managers import OptimizedMonthlyReportManager

    # Génération des données utilisateur avec cache optimisé
    users_data = []
    users = User.objects.filter(is_active=True).select_related("profile").all()

    # Utilisation du gestionnaire en bulk pour optimiser
    bulk_data = OptimizedMonthlyReportManager.get_bulk_monthly_data(users, year, month)

    for user in users:
        monthly_data = bulk_data.get(user.id, {})

        # Calcul solde congés avec get_leave_balance optimisé
        balance_info = get_leave_balance(user)

        # Ajouter les données calculées à l'utilisateur
        user.days_leave = monthly_data.get("days_leave", 0)
        user.days_telework = monthly_data.get("days_telework", 0)
        user.days_at_office = monthly_data.get("days_at_office", 0)
        user.balance = balance_info.get("balance", 0)
        user.from_cache = monthly_data.get("from_cache", False)

        users_data.append(user)

    # Données générales du rapport
    report_data = _generate_monthly_report_data(start_date, end_date)

    context = {
        "users": users_data,
        "year": year,
        "month": month,
        "selected_month": f"{year}-{month:02d}",
        "month_range": range(1, 13),
        "year_range": range(2020, date.today().year + 2),
        "start_date": start_date,
        "end_date": end_date,
        "report_data": report_data,
    }

    return render(request, "extranet/admin_monthly_report.html", context)


def _handle_user_creation(request):
    """Traite la création d'un nouvel utilisateur."""
    try:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Création du profil
            profile = UserProfile.objects.create(
                user=user,
                role=form.cleaned_data["role"],
                site=form.cleaned_data["site"],
            )

            logger.info(
                f"[user_admin] Utilisateur créé: {user.username} par {request.user.username}"
            )
            messages.success(request, f"Utilisateur {user.username} créé avec succès.")
            return True
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return False

    except Exception as e:
        logger.error(f"[user_admin] Erreur création utilisateur: {e}")
        messages.error(request, "Erreur lors de la création de l'utilisateur.")
        return False


def _handle_user_update(request):
    """Traite la mise à jour d'un utilisateur."""
    try:
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)

        # Mise à jour des informations de base
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")

        # Changement de mot de passe si fourni
        new_password = request.POST.get("password")
        if new_password:
            user.set_password(new_password)

        user.save()

        # Mise à jour du profil
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = request.POST.get("role", "user")
        profile.site = request.POST.get("site", "Tunisie")

        # Gestion du report de congés
        carry_over = request.POST.get("carry_over", "0")
        try:
            profile.carry_over = float(carry_over)
            if profile.carry_over < 0:
                profile.carry_over = 0
            elif profile.carry_over > 10:
                profile.carry_over = 10
        except (ValueError, TypeError):
            profile.carry_over = 0

        # Manager et RH
        manager_id = request.POST.get("manager")
        if manager_id:
            profile.manager = User.objects.get(id=manager_id)
        else:
            profile.manager = None

        rh_id = request.POST.get("rh")
        if rh_id:
            profile.rh = User.objects.get(id=rh_id)
        else:
            profile.rh = None

        profile.save()

        logger.info(
            f"[user_admin] Utilisateur mis à jour: {user.username} par {request.user.username}"
        )
        messages.success(request, f"Utilisateur {user.username} mis à jour.")
        return True

    except Exception as e:
        logger.error(f"[user_admin] Erreur mise à jour utilisateur: {e}")
        messages.error(request, "Erreur lors de la mise à jour.")
        return False


def _handle_user_deletion(request):
    """Traite la suppression d'un utilisateur."""
    try:
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)

        # Protection: ne pas supprimer son propre compte
        if user == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
            return False

        username = user.username
        user.delete()

        logger.info(
            f"[user_admin] Utilisateur supprimé: {username} par {request.user.username}"
        )
        messages.success(request, f"Utilisateur {username} supprimé.")
        return True

    except Exception as e:
        logger.error(f"[user_admin] Erreur suppression utilisateur: {e}")
        messages.error(request, "Erreur lors de la suppression.")
        return False


def _export_users_csv():
    """Exporte la liste des utilisateurs en CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="utilisateurs.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["Login", "Nom", "Prénom", "Email", "Rôle", "Site", "Manager", "RH"]
    )

    users = User.objects.select_related("profile").all()
    for user in users:
        profile = getattr(user, "profile", None)
        writer.writerow(
            [
                user.username,
                user.last_name,
                user.first_name,
                user.email,
                profile.get_role_display() if profile else "",
                profile.get_site_display() if profile else "",
                profile.manager.get_full_name() if profile and profile.manager else "",
                profile.rh.get_full_name() if profile and profile.rh else "",
            ]
        )

    return response


def _handle_leave_admin_action(request):
    """Traite les actions administratives sur les congés."""
    action = request.POST.get("action")
    leave_id = request.POST.get("leave_id")

    if action and leave_id:
        leave = get_object_or_404(LeaveRequest, id=leave_id)

        if action in ["approve", "reject"]:
            leave.status = "approved" if action == "approve" else "rejected"
            leave.admin_validated = True
            leave.admin_validated_at = timezone.now()
            leave.save()

            messages.success(request, f"Demande de congé {action} avec succès.")


def _handle_telework_admin_action(request):
    """Traite les actions administratives sur le télétravail."""
    action = request.POST.get("action")
    telework_id = request.POST.get("telework_id")

    if action and telework_id:
        telework = get_object_or_404(TeleworkRequest, id=telework_id)

        if action in ["approve", "reject"]:
            telework.status = "approved" if action == "approve" else "rejected"
            telework.admin_validated = True
            telework.admin_validated_at = timezone.now()
            telework.save()

            messages.success(request, f"Demande de télétravail {action} avec succès.")


def _calculate_leave_stats(leaves):
    """Calcule les statistiques des congés."""
    total = leaves.count()
    approved = leaves.filter(status="approved").count()
    pending = leaves.filter(status="pending").count()
    rejected = leaves.filter(status="rejected").count()

    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "approval_rate": (approved / total * 100) if total > 0 else 0,
    }


def _calculate_telework_stats(teleworks):
    """Calcule les statistiques du télétravail."""
    total = teleworks.count()
    approved = teleworks.filter(status="approved").count()
    pending = teleworks.filter(status="pending").count()
    rejected = teleworks.filter(status="rejected").count()

    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "approval_rate": (approved / total * 100) if total > 0 else 0,
    }


def _generate_monthly_report_data(start_date, end_date):
    """Génère les données du rapport mensuel."""
    # Congés de la période
    leaves = LeaveRequest.objects.filter(
        start_date__lte=end_date, end_date__gte=start_date
    )

    # Télétravail de la période
    teleworks = TeleworkRequest.objects.filter(
        start_date__lte=end_date, end_date__gte=start_date
    )

    # Statistiques générales
    total_users = User.objects.filter(is_active=True).count()

    return {
        "total_users": total_users,
        "leaves": {
            "total": leaves.count(),
            "approved": leaves.filter(status="approved").count(),
            "pending": leaves.filter(status="pending").count(),
            "rejected": leaves.filter(status="rejected").count(),
        },
        "teleworks": {
            "total": teleworks.count(),
            "approved": teleworks.filter(status="approved").count(),
            "pending": teleworks.filter(status="pending").count(),
            "rejected": teleworks.filter(status="rejected").count(),
        },
        "period": f"{start_date.strftime('%B %Y')}",
    }


@login_required
def validation(request):
    """Vue pour la validation des demandes de congés et télétravail par les managers et RH."""
    user = request.user
    type = request.GET.get("type", "leave")
    leaves = teleworks = []

    if hasattr(user, "profile"):
        role = user.profile.role

        # Déterminer si l'utilisateur peut faire les validations manager ET RH
        can_validate_as_manager = role in ["manager", "admin"]
        can_validate_as_rh = role in ["rh", "admin"]

        # Pour les congés
        if can_validate_as_manager and can_validate_as_rh:
            # Double rôle : voir toutes les demandes à valider
            leaves = LeaveRequest.objects.filter(
                Q(
                    status="pending",
                    user__profile__manager=user,
                    manager_validated=False,
                )
                | Q(
                    status="pending",
                    user__profile__rh=user,
                    manager_validated=True,
                    rh_validated=False,
                )
            ).distinct()
        elif can_validate_as_manager:
            # Manager uniquement
            leaves = LeaveRequest.objects.filter(
                status="pending", user__profile__manager=user, manager_validated=False
            )
        elif can_validate_as_rh:
            # RH uniquement
            leaves = LeaveRequest.objects.filter(
                status="pending",
                user__profile__rh=user,
                manager_validated=True,
                rh_validated=False,
            )

        # Pour les télétravaux (uniquement validation manager)
        if can_validate_as_manager:
            teleworks = TeleworkRequest.objects.filter(
                status="pending", user__profile__manager=user, manager_validated=False
            )

    # Traitement POST pour validation/rejet
    if request.method == "POST":
        if "leave_id" in request.POST:
            leave = LeaveRequest.objects.get(id=request.POST["leave_id"])
            action = request.POST.get("action")

            # Validation manager
            if (
                action == "manager_approve"
                and can_validate_as_manager
                and leave.user.profile.manager == user
                and not leave.manager_validated
            ):
                leave.manager_validated = True
                leave.save()
                messages.success(request, "Demande validée par le manager.")

            # Validation RH
            elif (
                action == "rh_approve"
                and can_validate_as_rh
                and leave.user.profile.rh == user
                and leave.manager_validated
                and not leave.rh_validated
            ):
                leave.rh_validated = True
                leave.status = "approved"
                leave.save()
                messages.success(request, "Demande validée par le RH.")

            # Rejet
            elif action == "reject":
                leave.status = "rejected"
                leave.save()
                messages.error(request, "Demande rejetée.")

            return redirect("extranet:validation")

        elif "tw_id" in request.POST:
            tw = TeleworkRequest.objects.get(id=request.POST["tw_id"])
            action = request.POST.get("action")

            if (
                action == "manager_approve"
                and can_validate_as_manager
                and tw.user.profile.manager == user
                and not tw.manager_validated
            ):
                tw.manager_validated = True
                tw.status = "approved"
                tw.save()
                messages.success(request, "Télétravail validé.")
            elif action == "reject":
                tw.status = "rejected"
                tw.save()
                messages.error(request, "Demande de télétravail rejetée.")

    # Calcul du nombre de validations en attente pour badge menu
    validation_count = 0
    if hasattr(request.user, "profile"):
        role = request.user.profile.role
        can_validate_as_manager = role in ["manager", "admin"]
        can_validate_as_rh = role in ["rh", "admin"]

        if can_validate_as_manager:
            # Compter les demandes en attente de validation manager
            validation_count += LeaveRequest.objects.filter(
                status="pending",
                user__profile__manager=request.user,
                manager_validated=False,
            ).count()
            validation_count += TeleworkRequest.objects.filter(
                status="pending",
                user__profile__manager=request.user,
                manager_validated=False,
            ).count()

        if can_validate_as_rh:
            # Compter les demandes en attente de validation RH
            validation_count += LeaveRequest.objects.filter(
                status="pending",
                user__profile__rh=request.user,
                manager_validated=True,
                rh_validated=False,
            ).count()

    return render(
        request,
        "extranet/validation.html",
        {
            "type": type,
            "leaves": leaves if type == "leave" else [],
            "teleworks": teleworks if type == "telework" else [],
            "validation_count": validation_count,
            "can_validate_as_manager": (
                can_validate_as_manager if hasattr(user, "profile") else False
            ),
            "can_validate_as_rh": (
                can_validate_as_rh if hasattr(user, "profile") else False
            ),
        },
    )
