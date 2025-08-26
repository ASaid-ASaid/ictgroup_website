"""
Vues d'administration pour la gestion des utilisateurs et rapports.
"""

import csv
import logging
import tempfile
import os
from datetime import date, timedelta
from io import StringIO
import sys

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import UserCreationForm
from ..models import LeaveRequest, TeleworkRequest, UserProfile, get_leave_balance, MonthlyUserStats

logger = logging.getLogger(__name__)


def is_admin_or_rh(user):
    """Vérifie si l'utilisateur est admin ou RH."""
    return hasattr(user, "profile") and user.profile.role in ["admin", "rh"]


def is_admin_rh_or_manager(user):
    """Vérifie si l'utilisateur est admin, RH ou manager."""
    return hasattr(user, "profile") and user.profile.role in ["admin", "rh", "manager"]


@login_required
@user_passes_test(is_admin_or_rh)
def user_admin(request):
    """Interface d'administration des utilisateurs."""

    # Traitement des actions POST
    if request.method == "POST":

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

    # Listes pour les dropdowns
    managers = users.filter(profile__role__in=['manager', 'admin']).order_by('first_name', 'last_name')
    rh_users = users.filter(profile__role__in=['rh', 'admin', 'manager']).order_by('first_name', 'last_name')

    context = {
        "users": users,
        "user_balances": user_balances,
        "managers": managers,
        "rh_users": rh_users,
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
@user_passes_test(is_admin_rh_or_manager)
def admin_monthly_report(request):
    """Rapport mensuel pour les RH/Admin - Utilise les nouveaux modèles UserLeaveBalance et MonthlyUserStats."""

    # Paramètres de période
    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))
    site_filter = request.GET.get("site", "")  # Nouveau filtre par site

    # Calcul des dates
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    # Génération des données utilisateur avec nouveaux modèles
    users_data = []
    users = User.objects.filter(is_active=True).select_related("profile")
    
    # Filtrage par site si spécifié
    if site_filter:
        users = users.filter(profile__site=site_filter)
    
    users = users.all()

    for user in users:
        # Récupération ou création des statistiques mensuelles
        stats, created = MonthlyUserStats.objects.get_or_create(
            user=user,
            year=year,
            month=month
        )
        
        # Si créé, mettre à jour depuis les demandes
        if created:
            stats.update_from_requests()

        # Calcul solde congés avec get_leave_balance optimisé
        balance_info = get_leave_balance(user)

        # Ajouter les données calculées à l'utilisateur
        user.days_leave = float(stats.days_leave)
        user.days_telework = stats.days_telework
        user.days_at_office = stats.days_at_office
        user.overtime_hours = float(stats.overtime_hours)
        user.leave_balance_remaining = float(balance_info.get("remaining", 0))
        user.total_workdays = stats.total_workdays

        users_data.append(user)

    # Données générales du rapport
    report_data = _generate_monthly_report_data(start_date, end_date)

    # Liste des sites disponibles pour le filtre
    available_sites = UserProfile.objects.filter(user__is_active=True).values_list('site', flat=True).distinct().order_by('site')

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
        "available_sites": available_sites,
        "selected_site": site_filter,
    }

    return render(request, "extranet/admin_monthly_report.html", context)


def _handle_user_creation(request):
    """Traite la création d'un nouvel utilisateur."""
    try:
        # Validation des champs obligatoires
        required_fields = ['username', 'first_name', 'last_name', 'email', 'password', 'role', 'site']
        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f"Le champ {field} est obligatoire.")
                return False

        # Création de l'utilisateur
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )

        # Récupération des références manager et rh
        manager = None
        if request.POST.get('manager'):
            try:
                manager = User.objects.get(id=request.POST['manager'])
            except User.DoesNotExist:
                pass

        rh = None
        if request.POST.get('rh'):
            try:
                rh = User.objects.get(id=request.POST['rh'])
            except User.DoesNotExist:
                pass

        # Création du profil
        UserProfile.objects.create(
            user=user,
            role=request.POST['role'],
            site=request.POST['site'],
            manager=manager,
            rh=rh
        )

        logger.info(
            f"[user_admin] Utilisateur créé: {user.username} par {request.user.username}"
        )
        messages.success(request, f"Utilisateur {user.username} créé avec succès.")
        return True

    except Exception as e:
        logger.error(f"[user_admin] Erreur création utilisateur: {e}")
        messages.error(request, f"Erreur lors de la création de l'utilisateur: {str(e)}")
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
        profile.site = request.POST.get("site", "tunisie")

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
        
        # Vérifier si l'utilisateur a des responsabilités RH (même s'il est manager)
        from ..models import UserProfile
        has_rh_responsibilities = UserProfile.objects.filter(rh=user).exists()
        
        # Déterminer si l'utilisateur peut faire les validations manager ET RH
        can_validate_as_manager = role in ["manager", "admin"]
        can_validate_as_rh = role in ["rh", "admin"] or has_rh_responsibilities

        # Pour les congés - nouvelle logique : validation en parallèle
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
                    manager_validated=True,  # RH valide après le manager
                    rh_validated=False,
                )
                | Q(
                    status="pending",
                    user=user,  # Ses propres demandes
                    manager_validated=False,
                )
            ).distinct()
        elif can_validate_as_manager:
            # Manager uniquement - ses subordonnés ET ses propres demandes
            leaves = LeaveRequest.objects.filter(
                status="pending", 
                manager_validated=False
            ).filter(
                Q(user__profile__manager=user) | Q(user=user)  # Subordonnés OU lui-même
            )
        elif can_validate_as_rh:
            # RH uniquement - ses subordonnés ET ses propres demandes (après validation manager)
            leaves = LeaveRequest.objects.filter(
                status="pending", 
                manager_validated=True,  # RH valide après le manager
                rh_validated=False
            ).filter(
                Q(user__profile__rh=user) | Q(user=user)  # Subordonnés OU lui-même
            )

        # Pour les télétravaux - maintenant avec validation manager ET RH
        if can_validate_as_manager and can_validate_as_rh:
            # Double rôle : voir toutes les demandes à valider
            teleworks = TeleworkRequest.objects.filter(
                Q(
                    status="pending",
                    user__profile__manager=user,
                    manager_validated=False,
                )
                | Q(
                    status="pending",
                    user__profile__rh=user,
                    rh_validated=False,
                )
                | Q(
                    status="pending",
                    user=user,  # Ses propres demandes
                    manager_validated=False,
                )
            ).distinct()
        elif can_validate_as_manager:
            # Manager uniquement - ses subordonnés ET ses propres demandes
            teleworks = TeleworkRequest.objects.filter(
                status="pending", 
                manager_validated=False
            ).filter(
                Q(user__profile__manager=user) | Q(user=user)  # Subordonnés OU lui-même
            )
        elif can_validate_as_rh:
            # RH uniquement
            teleworks = TeleworkRequest.objects.filter(
                status="pending", user__profile__rh=user, rh_validated=False
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
                and (leave.user.profile.manager == user or leave.user == user)  # Subordonnés OU lui-même
                and not leave.manager_validated
            ):
                leave.manager_validated = True
                # Approuver si les deux validations sont faites
                if leave.rh_validated:
                    leave.status = "approved"
                leave.save()
                messages.success(request, "Demande validée par le manager.")

            # Validation RH
            elif (
                action == "rh_approve"
                and can_validate_as_rh
                and (leave.user.profile.rh == user or leave.user == user)  # Subordonnés OU lui-même
                and leave.manager_validated  # RH valide après le manager
                and not leave.rh_validated
            ):
                leave.rh_validated = True
                # Approuver si les deux validations sont faites
                if leave.manager_validated:
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

            # Validation manager
            if (
                action == "manager_approve"
                and can_validate_as_manager
                and (tw.user.profile.manager == user or tw.user == user)  # Subordonnés OU lui-même
                and not tw.manager_validated
            ):
                tw.manager_validated = True
                # Approuver si les deux validations sont faites
                if tw.rh_validated:
                    tw.status = "approved"
                tw.save()
                messages.success(request, "Télétravail validé par le manager.")

            # Validation RH
            elif (
                action == "rh_approve"
                and can_validate_as_rh
                and tw.user.profile.rh == user
                and not tw.rh_validated
            ):
                tw.rh_validated = True
                # Approuver si les deux validations sont faites
                if tw.manager_validated:
                    tw.status = "approved"
                tw.save()
                messages.success(request, "Télétravail validé par le RH.")

            # Rejet
            elif action == "reject":
                tw.status = "rejected"
                tw.save()
                messages.error(request, "Demande de télétravail rejetée.")

    # Calcul du nombre de validations en attente pour badge menu
    validation_count = 0
    if hasattr(request.user, "profile"):
        role = request.user.profile.role
        # Vérifier si l'utilisateur a des responsabilités RH (même s'il est manager)
        from ..models import UserProfile
        has_rh_responsibilities = UserProfile.objects.filter(rh=request.user).exists()
        
        can_validate_as_manager = role in ["manager", "admin"]
        can_validate_as_rh = role in ["rh", "admin"] or has_rh_responsibilities

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
                manager_validated=True,  # Seulement les demandes déjà validées par le manager
                rh_validated=False,
            ).count()
            validation_count += TeleworkRequest.objects.filter(
                status="pending",
                user__profile__rh=request.user,
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


@login_required
@user_passes_test(is_admin_or_rh)
def import_users_csv(request):
    """Interface d'import CSV des utilisateurs."""
    
    if request.method == "POST":
        # Vérifier si un fichier a été uploadé
        if 'csv_file' not in request.FILES:
            messages.error(request, "Aucun fichier sélectionné.")
            return redirect("extranet:user_admin")
        
        csv_file = request.FILES['csv_file']
        
        # Vérifier l'extension du fichier
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Le fichier doit être au format CSV.")
            return redirect("extranet:user_admin")
        
        # Vérifier la taille du fichier (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            messages.error(request, "Le fichier est trop volumineux (max 5MB).")
            return redirect("extranet:user_admin")
        
        try:
            # Sauvegarder temporairement le fichier
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
                for chunk in csv_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Mode simulation si demandé
            simulate = request.POST.get('simulate') == 'on'
            
            # Appeler la commande d'import
            try:
                if simulate:
                    # Capturer la sortie de la commande pour la simulation
                    from io import StringIO
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()
                    
                    try:
                        call_command('import_update_users', '--file', temp_file_path, '--dry-run')
                        
                        # Restaurer stdout
                        sys.stdout = old_stdout
                        command_output = captured_output.getvalue()
                        
                        # Créer un fichier de rapport téléchargeable
                        response = HttpResponse(command_output, content_type='text/plain; charset=utf-8')
                        response['Content-Disposition'] = f'attachment; filename="simulation_import_{date.today().strftime("%Y%m%d")}.txt"'
                        
                        # Supprimer le fichier temporaire
                        try:
                            os.unlink(temp_file_path)
                        except OSError:
                            pass
                            
                        return response
                        
                    except Exception as e:
                        sys.stdout = old_stdout
                        raise e
                else:
                    call_command('import_update_users', '--file', temp_file_path)
                    messages.success(request, 
                        "🎉 Import terminé avec succès ! Les utilisateurs ont été créés/mis à jour.")
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'import CSV: {str(e)}")
                messages.error(request, f"Erreur lors de l'import : {str(e)}")
            
            # Supprimer le fichier temporaire
            os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier CSV: {str(e)}")
            messages.error(request, f"Erreur lors du traitement du fichier : {str(e)}")
    
    return redirect("extranet:user_admin")
