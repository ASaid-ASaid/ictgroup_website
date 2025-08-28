"""
Vues de gestion des demandes de congé.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import logging

from ..models import LeaveRequest, UserProfile, MonthlyUserStats
from ..forms import LeaveRequestForm
from ..utils import get_cached_leave_balance

logger = logging.getLogger(__name__)


@login_required
def leave_request(request):
    """Permet à l'utilisateur de soumettre une nouvelle demande de congé."""
    logger.info(f"[leave_request] Demande par {request.user.username} (méthode: {request.method})")
    
    if request.method == "POST":
        form = LeaveRequestForm(request.POST, user=request.user)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            
            # Gestion des conflits avec télétravail approuvés
            # Les congés ont priorité et annulent automatiquement les télétravails
            if hasattr(form, 'conflicting_teleworks'):
                from ..models import TeleworkRequest
                conflicting_teleworks = TeleworkRequest.objects.filter(
                    user=request.user,
                    status='approved',
                    start_date__lte=leave_request.end_date,
                    end_date__gte=leave_request.start_date
                )
                
                if conflicting_teleworks.exists():
                    cancelled_count = 0
                    cancelled_details = []
                    
                    for telework in conflicting_teleworks:
                        telework.status = 'cancelled'
                        telework.save()
                        cancelled_count += 1
                        cancelled_details.append(f"#{telework.id} ({telework.start_date.strftime('%d/%m/%Y')} - {telework.end_date.strftime('%d/%m/%Y')})")
                        logger.info(f"[leave_request] Télétravail #{telework.id} annulé automatiquement par congé #{leave_request.id}")
                    
                    # Message informatif pour l'utilisateur
                    if cancelled_count > 0:
                        details = ", ".join(cancelled_details)
                        messages.warning(
                            request, 
                            f"⚠️ Attention : {cancelled_count} demande(s) de télétravail ont été automatiquement annulées "
                            f"car les congés ont priorité : {details}. "
                            f"Vous pouvez créer de nouvelles demandes de télétravail pour d'autres dates."
                        )
            
            logger.info(f"[leave_request] Demande créée pour {request.user.username}: {leave_request.start_date} - {leave_request.end_date}")
            messages.success(request, "Votre demande de congé a été soumise avec succès.")
            return redirect("extranet:leave_list")
        else:
            logger.warning(f"[leave_request] Erreurs de validation pour {request.user.username}: {form.errors}")
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = LeaveRequestForm(user=request.user)
    
    # Calcul du solde de congés
    leave_balance = get_cached_leave_balance(request.user)
    
    context = {
        'form': form,
        'leave_balance': leave_balance,
    }
    
    return render(request, 'extranet/leave_request.html', context)


@login_required
def leave_list(request):
    """Affiche la liste des demandes de congé de l'utilisateur."""
    user = request.user
    
    # Récupération des demandes de l'utilisateur
    leaves = LeaveRequest.objects.filter(user=user).order_by('-submitted_at')
    
    # Filtrage par statut si demandé
    status_filter = request.GET.get('status')
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    
    # Calcul du solde de congés
    leave_balance = get_cached_leave_balance(user)
    
    context = {
        'leaves': leaves,
        'leave_requests': leaves,  # Pour compatibilité avec le template
        'leave_balance': leave_balance,
        'status_filter': status_filter,
        'status_choices': LeaveRequest.STATUS_CHOICES,
    }
    
    return render(request, 'extranet/leave_list.html', context)


def can_validate_leaves(user):
    """Vérifie si l'utilisateur peut valider des demandes de congé."""
    return (hasattr(user, 'profile') and 
            user.profile.role in ['manager', 'rh', 'admin'])


@login_required
@user_passes_test(can_validate_leaves)
def validate_leave(request):
    """Interface de validation des demandes de congé."""
    user = request.user
    
    # Traitement des actions POST
    if request.method == 'POST':
        action = request.POST.get('action')
        leave_id = request.POST.get('leave_id')
        validation_type = request.POST.get('validation_type')  # 'manager' ou 'rh'
        
        if action and leave_id and validation_type:
            leave_request = get_object_or_404(LeaveRequest, id=leave_id)
            
            # Vérification des permissions de validation
            if _can_user_validate_leave(user, leave_request, validation_type):
                success = _process_leave_validation(user, leave_request, action, validation_type)
                if success:
                    validation_label = "manager" if validation_type == "manager" else "RH"
                    messages.success(request, f"Demande de congé {action} par {validation_label} avec succès.")
                else:
                    messages.error(request, "Erreur lors du traitement de la demande.")
            else:
                messages.error(request, "Vous n'avez pas les permissions pour traiter cette demande.")
                
            return redirect('extranet:validate_leave')
    
    # Récupération des demandes à valider
    pending_leaves = _get_leaves_to_validate(user)
    
    # Variables pour les permissions dans le template
    can_validate_as_manager = hasattr(user, 'profile') and user.profile.is_manager()
    can_validate_as_rh = hasattr(user, 'profile') and user.profile.is_rh()
    
    context = {
        'leaves': pending_leaves,  # Utilisé par le template
        'pending_leaves': pending_leaves,
        'user_role': user.profile.role if hasattr(user, 'profile') else None,
        'can_validate_as_manager': can_validate_as_manager,
        'can_validate_as_rh': can_validate_as_rh,
        'type': request.GET.get('type', 'leave'),  # Par défaut, afficher les congés
    }
    
    return render(request, 'extranet/validation.html', context)


@login_required
def leave_edit(request, leave_id):
    """Permet de modifier une demande de congé."""
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Vérifier les permissions : propriétaire ou validateur
    if (leave_request.user != request.user and 
        not (hasattr(request.user, 'profile') and 
             request.user.profile.role in ['admin', 'manager', 'rh'])):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette demande.")
        return redirect('extranet:leave_list')
    
    # Ne peut être modifiée que si elle est en attente (sauf pour les validateurs)
    if (leave_request.status != 'pending' and 
        not (hasattr(request.user, 'profile') and 
             request.user.profile.role in ['admin', 'manager', 'rh'])):
        messages.error(request, "Cette demande ne peut plus être modifiée.")
        return redirect('extranet:leave_list')
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request, user=leave_request.user)
        if form.is_valid():
            # Réinitialiser les validations si la demande est modifiée
            if leave_request.user == request.user:  # Si c'est le propriétaire qui modifie
                leave_request.manager_validated = False
                leave_request.rh_validated = False
                leave_request.status = 'pending'
            
            form.save()
            messages.success(request, "Demande de congé modifiée avec succès.")
            return redirect('extranet:leave_list')
    else:
        form = LeaveRequestForm(instance=leave_request, user=leave_request.user)
    
    # Calcul du solde de congés
    leave_balance = get_cached_leave_balance(request.user)
    
    return render(request, 'extranet/leave_edit.html', {
        'form': form,
        'leave_request': leave_request,
        'leave_balance': leave_balance,
    })


@login_required
def leave_delete(request, leave_id):
    """Permet de supprimer une demande de congé."""
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Vérifier les permissions : propriétaire ou validateur
    if (leave_request.user != request.user and 
        not (hasattr(request.user, 'profile') and 
             request.user.profile.role in ['admin', 'manager', 'rh'])):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette demande.")
        return redirect('extranet:leave_list')
    
    # Ne peut être supprimée que si elle est en attente ou rejetée
    if leave_request.status == 'approved':
        messages.error(request, "Une demande approuvée ne peut pas être supprimée.")
        return redirect('extranet:leave_list')
    
    if request.method == 'POST':
        leave_request.delete()
        messages.success(request, "Demande de congé supprimée avec succès.")
        return redirect('extranet:leave_list')
    
    return render(request, 'extranet/leave_delete.html', {
        'leave_request': leave_request,
    })


@login_required
@user_passes_test(can_validate_leaves)
def monthly_leave_report(request):
    """Rapport mensuel des congés - accessible aux managers, RH et admin."""
    from datetime import date, timedelta
    
    # Paramètres de période
    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))
    site_filter = request.GET.get("site", "")  # Filtre par site

    # Calcul des dates
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    # Génération des données utilisateur
    users_data = []
    users = User.objects.filter(is_active=True).select_related("profile")
    
    # Filtrage par site si spécifié
    if site_filter:
        users = users.filter(profile__site=site_filter)
    
    # Filtrage selon le rôle de l'utilisateur
    if request.user.profile.role == 'manager':
        # Les managers ne voient que leurs subordonnés + eux-mêmes
        users = users.filter(
            Q(profile__manager=request.user) | Q(id=request.user.id)
        )
    elif request.user.profile.role == 'rh':
        # Les RH voient les utilisateurs dont ils sont RH
        users = users.filter(profile__rh=request.user)
    # Les admins voient tout
    
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

        # Calcul solde congés
        balance_info = get_cached_leave_balance(user)

        # Ajouter les données calculées à l'utilisateur
        user.days_leave = float(stats.days_leave)
        user.days_telework = stats.days_telework
        user.days_at_office = stats.days_at_office
        user.overtime_hours = float(stats.overtime_hours)
        user.leave_balance_remaining = float(balance_info.get("remaining", 0))
        user.total_workdays = stats.total_workdays
        user.site_display = user.profile.get_site_display() if hasattr(user, 'profile') else 'N/A'

        users_data.append(user)

    # Liste des sites disponibles pour le filtre
    available_sites = UserProfile.objects.filter(user__is_active=True).values_list('site', flat=True).distinct().order_by('site')

    # Calcul des totaux pour les statistiques globales
    total_leave_days = sum(user.days_leave for user in users_data)
    total_telework_days = sum(user.days_telework for user in users_data)
    total_overtime_hours = sum(user.overtime_hours for user in users_data)

    context = {
        "users": users_data,
        "year": year,
        "month": month,
        "selected_month": f"{year}-{month:02d}",
        "month_range": range(1, 13),
        "year_range": range(2020, date.today().year + 2),
        "start_date": start_date,
        "end_date": end_date,
        "available_sites": available_sites,
        "selected_site": site_filter,
        # Totaux pour les statistiques globales
        "total_leave_days": total_leave_days,
        "total_telework_days": total_telework_days,
        "total_overtime_hours": total_overtime_hours,
    }

    return render(request, "extranet/monthly_leave_report.html", context)


def _can_user_validate_leave(user, leave_request, validation_type=None):
    """Vérifie si l'utilisateur peut valider une demande spécifique."""
    if not hasattr(user, 'profile'):
        return False
    
    role = user.profile.role
    
    if role == 'admin':
        return True
    
    # Validation spécifique par type
    if validation_type == 'manager':
        return (
            user.profile.is_manager() and 
            leave_request.user.profile.manager == user and 
            not leave_request.manager_validated
        )
    elif validation_type == 'rh':
        return (
            user.profile.is_rh() and
            leave_request.user.profile.rh == user and 
            leave_request.manager_validated and 
            not leave_request.rh_validated
        )
    
    # Si pas de type spécifié, vérifier les permissions selon les rôles multiples
    can_validate_as_manager = (
        user.profile.is_manager() and 
        leave_request.user.profile.manager == user and 
        not leave_request.manager_validated
    )
    
    can_validate_as_rh = (
        user.profile.is_rh() and
        leave_request.user.profile.rh == user and 
        leave_request.manager_validated and 
        not leave_request.rh_validated
    )
    
    return can_validate_as_manager or can_validate_as_rh


def _process_leave_validation(user, leave_request, action, validation_type=None):
    """Traite la validation ou le rejet d'une demande de congé."""
    try:
        role = user.profile.role
        
        if action == 'approve':
            # Validation spécifique par type ou détermination automatique
            if validation_type == 'manager' or (validation_type is None and 
                user.profile.is_manager() and 
                leave_request.user.profile.manager == user and 
                not leave_request.manager_validated):
                # Validation en tant que Manager
                leave_request.manager_validated = True
                leave_request.manager_validated_at = timezone.now()
                leave_request.manager_comment = ""
                
                # Si pas de RH assigné, approuver directement
                if not leave_request.user.profile.rh:
                    leave_request.status = 'approved'
                    
            elif validation_type == 'rh' or (validation_type is None and
                  user.profile.is_rh() and
                  leave_request.user.profile.rh == user and
                  leave_request.manager_validated and
                  not leave_request.rh_validated):
                # Validation en tant que RH
                leave_request.rh_validated = True
                leave_request.rh_validated_at = timezone.now()
                leave_request.status = 'approved'
                
            elif role == 'admin':
                # Admin peut tout valider directement
                leave_request.admin_validated = True
                leave_request.admin_validated_at = timezone.now()
                leave_request.status = 'approved'
                
        elif action == 'reject':
            leave_request.status = 'rejected'
            
            # Déterminer le type de commentaire selon le rôle de validation
            if validation_type == 'manager' or (
                user.profile.is_manager() and 
                leave_request.user.profile.manager == user and
                not leave_request.manager_validated):
                leave_request.manager_comment = "Rejetée par le manager"
            elif validation_type == 'rh' or (
                  user.profile.is_rh() and
                  leave_request.user.profile.rh == user):
                leave_request.rh_comment = "Rejetée par les RH"
                
        leave_request.save()
        
        logger.info(f"[validate_leave] Demande {leave_request.id} {action} par {user.username}")
        return True
        
    except Exception as e:
        logger.error(f"[validate_leave] Erreur lors du traitement: {e}")
        return False


def _get_leaves_to_validate(user):
    """Récupère les demandes de congé que l'utilisateur peut valider."""
    if not hasattr(user, 'profile'):
        return LeaveRequest.objects.none()
    
    role = user.profile.role
    
    if role == 'admin':
        return LeaveRequest.objects.filter(status='pending').order_by('-submitted_at')
    
    # Récupérer toutes les demandes potentielles selon les rôles multiples
    queryset = LeaveRequest.objects.none()
    
    # En tant que Manager : demandes des subordonnés (y compris ses propres demandes si il est son propre manager)
    if user.profile.is_manager():
        manager_requests = LeaveRequest.objects.filter(
            status='pending',
            user__profile__manager=user,
            manager_validated=False
        )
        queryset = queryset | manager_requests
    
    # En tant que RH : demandes où validation manager faite et RH pas encore faite
    if user.profile.is_rh():
        rh_requests = LeaveRequest.objects.filter(
            status='pending',
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False
        )
        queryset = queryset | rh_requests
    
    return queryset.distinct().order_by('-submitted_at')


@login_required
def admin_leaves(request):
    """Administration des congés."""
    messages.info(request, "Fonctionnalité en cours d'implémentation")
    return redirect('extranet:calendar_view')
