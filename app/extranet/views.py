# =====================
# Vues principales de l'app 'extranet'
# Chaque fonction ou classe gère une logique métier et retourne une réponse HTTP
# =====================

# Importation des modules nécessaires de Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.contrib.auth.models import User
from .models import LeaveRequest, TeleworkRequest, UserProfile, get_leave_balance
from django import forms
from django.contrib import messages
import logging
from datetime import date, timedelta
from django.db.models import Sum, F
import calendar
from datetime import date, timedelta, datetime
from workalendar.europe import France
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
import csv
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Configuration du logger
logger = logging.getLogger(__name__)

# =====================
# Formulaires
# =====================

# Formulaire pour la demande de congé
class LeaveRequestForm(forms.ModelForm):
    demi_jour = forms.ChoiceField(
        choices=LeaveRequest.DEMI_JOUR_CHOICES,
        widget=forms.RadioSelect,
        label="Demi-journée"
    )
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason', 'demi_jour']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2'}),
        }
        labels = {
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'reason': 'Raison de la demande (optionnel)',
            'demi_jour': 'Demi-journée',
        }

# Formulaire pour la demande de télétravail
class TeleworkRequestForm(forms.ModelForm):
    class Meta:
        model = TeleworkRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2'}),
        }
        labels = {
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'reason': 'Motif (optionnel)',
        }

    def clean(self):
        # Validation personnalisée pour s'assurer que la date de fin >= date de début
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'La date de fin doit être après la date de début.')
        return cleaned_data

# =====================
# Vues principales
# =====================

# Vue pour soumettre une demande de congé
@login_required
def leave_request_form(request):
    """Permet à l'utilisateur de soumettre une nouvelle demande de congé."""
    logger.info(f"[leave_request_form] Appel par {request.user if request.user.is_authenticated else 'anonyme'} (POST={request.method == 'POST'})")
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            logger.info(f"[leave_request_form] Demande de congé créée pour {request.user} du {leave_request.start_date} au {leave_request.end_date}")
            messages.success(request, 'Votre demande de congé a été soumise avec succès.')
            return redirect('extranet:leave_list')
        else:
            logger.warning(f"[leave_request_form] Erreur de validation pour {request.user}: {form.errors}")
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = LeaveRequestForm()
    return render(request, 'extranet/leave_request.html', {'form': form})

# Vue pour afficher la liste des demandes de congé
@login_required
# Vue pour afficher la liste des demandes de congé
# Updated leave_list view to handle leave day calculations in the backend
def leave_list(request):
    """Affiche la liste des demandes de congé de l'utilisateur (ou toutes pour l'admin)."""
    logger.info(f"[leave_list] Appel par {request.user}")
    if request.user.is_superuser:
        leave_requests = LeaveRequest.objects.all()
        leave_balance = None
        leave_taken = None
    else:
        leave_requests = LeaveRequest.objects.filter(user=request.user)
        today = date.today()
        months = (today.year - request.user.date_joined.year) * 12 + today.month - request.user.date_joined.month + 1
        accrued = months * 1.8
        taken = sum([
            0.5 if lr.demi_jour != 'full' and lr.start_date == lr.end_date else (lr.end_date - lr.start_date).days + 1
            for lr in leave_requests.filter(status='approved', start_date__year=today.year)
        ])
        leave_taken = taken
        leave_balance = accrued - leave_taken

    # Calcul des jours pour chaque demande
    for leave in leave_requests:
        leave.nb_days = 0.5 if leave.demi_jour != 'full' and leave.start_date == leave.end_date else (leave.end_date - leave.start_date).days + 1

    return render(request, 'extranet/leave_list.html', {
        'leave_requests': leave_requests,
        'leave_balance': leave_balance,
        'leave_taken': leave_taken,
    })

# Vue pour soumettre une demande de télétravail
@login_required
def telework_request_form(request):
    """Permet à l'utilisateur de soumettre une nouvelle demande de télétravail."""
    logger.info(f"[telework_request_form] Appel par {request.user if request.user.is_authenticated else 'anonyme'} (POST={request.method == 'POST'})")
    if request.method == 'POST':
        form = TeleworkRequestForm(request.POST)
        if form.is_valid():
            telework_request = form.save(commit=False)
            telework_request.user = request.user
            telework_request.save()
            logger.info(f"[telework_request_form] Demande de télétravail créée pour {request.user} du {telework_request.start_date} au {telework_request.end_date}")
            messages.success(request, 'Votre demande de télétravail a été soumise avec succès.')
            return redirect('extranet:telework_list')
        else:
            logger.warning(f"[telework_request_form] Erreur de validation pour {request.user}: {form.errors}")
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = TeleworkRequestForm()
    return render(request, 'extranet/telework_request.html', {'form': form})

# Vue pour afficher la liste des demandes de télétravail
@login_required
def telework_list(request):
    """Affiche la liste des demandes de télétravail de l'utilisateur (ou toutes pour l'admin)."""
    logger.info(f"[telework_list] Appel par {request.user}")
    if request.user.is_superuser:
        telework_requests = TeleworkRequest.objects.all()
    else:
        telework_requests = TeleworkRequest.objects.filter(user=request.user)
    return render(request, 'extranet/telework_list.html', {'telework_requests': telework_requests})

# Vue pour mettre à jour le statut d'une demande de congé
@login_required
def update_leave_status(request, pk):
    """Permet à l'admin de valider ou refuser une demande de congé."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    logger.info(f"[update_leave_status] Appel par {request.user} pour la demande {pk}")
    if not request.user.is_superuser:
        logger.warning(f"[update_leave_status] Accès refusé à {request.user}")
        messages.error(request, "Vous n'avez pas la permission de modifier le statut des demandes de congés.")
        return redirect('extranet:leave_list')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in LeaveRequest.STATUS_CHOICES]:
            leave_request.status = new_status
            leave_request.save()
            logger.info(f"[update_leave_status] Statut de la demande {pk} mis à jour à {new_status} par {request.user}")
            messages.success(request, f"Le statut de la demande a été mis à jour à '{new_status}'.")
        else:
            logger.warning(f"[update_leave_status] Statut invalide '{new_status}' pour la demande {pk} par {request.user}")
            messages.error(request, "Statut invalide.")
    return redirect('extranet:leave_list')

# Vue pour afficher le calendrier de présence
@login_required
def presence_calendar(request):
    """Affiche le calendrier mensuel de présence (congés, télétravail, fériés, week-ends, jours au bureau)."""
    user = request.user
    today = date.today()
    # Mode global si superuser/admin/manager/rh et paramètre global présent
    mode = request.GET.get('mode', 'me')
    user_id = request.GET.get('user_id')
    selected_user = user
    users = None
    can_see_global = user.is_superuser or (hasattr(user, 'profile') and getattr(user.profile, 'role', None) in ['admin', 'manager', 'rh'])
    if mode == 'global' and can_see_global:
        users = User.objects.all().order_by('last_name', 'first_name')
        if user_id:
            try:
                selected_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                selected_user = user
    # Récupère séparément mois et année depuis les menus déroulants
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        year = int(year)
        month = int(month)
    else:
        year, month = today.year, today.month
    # Pour le selecteur de mois/année
    year_range = list(range(today.year-1, today.year+2))
    month_range = list(range(1, 13))
    cal = calendar.Calendar(firstweekday=0)  # Lundi
    cal_days = list(cal.itermonthdates(year, month))
    cal_fr = France()
    holidays = set(dt for dt, _ in cal_fr.holidays(year))
    if can_see_global and (mode == 'global' and users or user.is_superuser):
        leaves = LeaveRequest.objects.filter(user=selected_user, start_date__year=year, start_date__month=month, status='approved')
        teleworks = TeleworkRequest.objects.filter(user=selected_user, start_date__year=year, start_date__month=month, status='approved')
    else:
        leaves = LeaveRequest.objects.filter(user=user, start_date__year=year, start_date__month=month, status='approved')
        teleworks = TeleworkRequest.objects.filter(user=user, start_date__year=year, start_date__month=month, status='approved')
    leave_days = set()
    demi_jour_days = {}
    for leave in leaves:
        if leave.demi_jour != 'full' and leave.start_date == leave.end_date:
            demi_jour_days[leave.start_date] = leave.demi_jour
            leave_days.add(leave.start_date)
        else:
            for n in range((leave.end_date - leave.start_date).days + 1):
                leave_days.add(leave.start_date + timedelta(days=n))
    telework_days = set()
    for tw in teleworks:
        for n in range((tw.end_date - tw.start_date).days + 1):
            telework_days.add(tw.start_date + timedelta(days=n))
    weeks = []
    week = []
    for d in cal_days:
        if d.month != month:
            week.append(None)
        else:
            day_info = {
                'day': d.day,
                'is_today': d == today and selected_user == user,
                'is_holiday': d in holidays,
                'is_leave': d in leave_days,
                'is_telework': d in telework_days,
                'is_weekend': d.weekday() >= 5,
                'demi_jour': demi_jour_days.get(d, None)
            }
            week.append(day_info)
        if len(week) == 7:
            weeks.append(week)
            week = []
    workdays = [d for d in cal_days if d.month == month and d.weekday() < 5 and d not in holidays]
    days_at_office = sum(1 for d in workdays if d not in leave_days and d not in telework_days and d <= today)
    holidays_count = sum(1 for d in cal_days if d.month == month and d in holidays)
    leaves_count = sum(1 for d in cal_days if d.month == month and d in leave_days)
    telework_count = sum(1 for d in cal_days if d.month == month and d in telework_days)
    weekends_count = sum(1 for d in cal_days if d.month == month and d.weekday() >= 5)
    # selected_month pour compatibilité template
    selected_month = f"{year:04d}-{month:02d}"
    return render(request, 'extranet/calendar.html', {
        'calendar': weeks,
        'selected_month': selected_month,
        'days_at_office': days_at_office,
        'holidays_count': holidays_count,
        'leaves_count': leaves_count,
        'telework_count': telework_count,
        'weekends_count': weekends_count,
        'year_range': year_range,
        'month_range': month_range,
        'mode': mode,
        'users': users,
        'selected_user': selected_user,
        'can_see_global': can_see_global,
    })

# Vue pour les paramètres du compte utilisateur
@login_required
def account_settings(request):
    """Permet à l'utilisateur de voir et modifier son email, mot de passe, site et solde de congés."""
    user = request.user  # Récupère l'utilisateur connecté
    leave_balance = get_leave_balance(user)
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        # Récupère les champs du formulaire
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        site = request.POST.get('site')
        changed = False
        # Vérification et mise à jour de l'email
        if email and email != user.email:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)
                user.email = email
                changed = True
            except ValidationError:
                messages.error(request, "L'adresse email n'est pas valide.")
        # Vérification et mise à jour du mot de passe
        if password:
            if password == password2:
                if len(password) < 8:
                    messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
                else:
                    user.set_password(password)
                    update_session_auth_hash(request, user)
                    changed = True
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
        # Mise à jour du site
        if profile and site and site.lower() != profile.site:
            profile.site = site.lower()
            profile.save()
            changed = True
        # Sauvegarde si modification
        if changed:
            user.save()
            messages.success(request, "Votre compte a été mis à jour.")
        elif request.method == 'POST' and not messages.get_messages(request):
            messages.info(request, "Aucune modification détectée.")
    return render(request, 'extranet/account_settings.html', {
        'email': user.email,
        'leave_balance': leave_balance,
        'profile': profile,
    })

# Vue pour la validation des demandes de télétravail (manager, RH, admin)
@login_required
def telework_validation(request):
    user = request.user
    # Affiche les demandes à valider selon le rôle
    if hasattr(user, 'profile') and user.profile.role in ['manager', 'rh', 'admin']:
        # Manager : demandes de ses subordonnés + ses propres TT, RH : tous sauf les siens, Admin : tous
        if user.profile.role == 'manager':
            telework_requests = TeleworkRequest.objects.filter(
                Q(user__profile__manager=user) | Q(user=user), status='pending'
            )
        elif user.profile.role == 'rh':
            telework_requests = TeleworkRequest.objects.filter(status='pending').exclude(user=user)
        else:  # admin
            telework_requests = TeleworkRequest.objects.filter(status='pending')
    else:
        telework_requests = TeleworkRequest.objects.none()
    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        action = request.POST.get('action')
        tw = TeleworkRequest.objects.get(id=req_id)
        if action == 'approve':
            tw.status = 'approved'
            tw.manager_validated = True
            tw.save()
            messages.success(request, 'Demande approuvée.')
        elif action == 'reject':
            tw.status = 'rejected'
            tw.save()
            messages.error(request, 'Demande rejetée.')
        return redirect('extranet:telework_validation')
    return render(request, 'extranet/telework_validation.html', {'telework_requests': telework_requests})

# Vue d'administration des utilisateurs (CRUD)
@login_required
def user_admin(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('extranet:leave_list')
    users = User.objects.all().select_related('profile')
    # Calcul du solde de congés pour chaque utilisateur
    user_balances = {user.id: get_leave_balance(user) for user in users}
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="utilisateurs_ictgroup.csv"'
        writer = csv.writer(response)
        writer.writerow(['Login', 'Nom', 'Prénom', 'Email', 'Rôle', 'Manager', 'RH', 'Acquis', 'Pris', 'Solde', 'Report'])
        for user in users:
            profile = getattr(user, 'profile', None)
            bal = user_balances.get(user.id, {})
            writer.writerow([
                user.username,
                user.last_name,
                user.first_name,
                user.email,
                profile.role if profile else '',
                profile.manager.get_full_name() if profile and profile.manager else '',
                profile.rh.get_full_name() if profile and profile.rh else '',
                bal.get('acquired', ''),
                bal.get('taken', ''),
                bal.get('balance', ''),
                bal.get('report', ''),
            ])
        return response
    # managers = UserProfile.objects.filter(role='manager')
    # rhs = UserProfile.objects.filter(role='rh')
    # On passe tous les users pour les listes déroulantes
    if request.method == 'POST':
        if request.POST.get('add_user'):
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            role = request.POST.get('role')
            manager_id = request.POST.get('manager')
            rh_id = request.POST.get('rh')
            if User.objects.filter(username=username).exists():
                messages.error(request, "Ce login existe déjà.")
            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                profile = UserProfile.objects.create(user=user, role=role)
                if manager_id:
                    profile.manager = User.objects.get(id=manager_id)
                if rh_id:
                    profile.rh = User.objects.get(id=rh_id)
                profile.save()
                messages.success(request, "Nouvel utilisateur ajouté.")
            return redirect('extranet:user_admin')
        elif request.POST.get('delete_user'):
            user_id = request.POST.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                if user.is_superuser:
                    messages.error(request, "Impossible de supprimer un superutilisateur.")
                else:
                    user.delete()
                    messages.success(request, "Utilisateur supprimé.")
            return redirect('extranet:user_admin')
        elif request.POST.get('user_id'):
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=user)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            if request.POST.get('password'):
                user.set_password(request.POST.get('password'))
            user.save()
            profile.role = request.POST.get('role')
            profile.site = request.POST.get('site').lower() if request.POST.get('site') else profile.site
            manager_id = request.POST.get('manager')
            rh_id = request.POST.get('rh')
            profile.manager = User.objects.get(id=manager_id) if manager_id else None
            profile.rh = User.objects.get(id=rh_id) if rh_id else None
            profile.save()
            messages.success(request, "Utilisateur modifié.")
        return redirect('extranet:user_admin')
    # Calcul du nombre de validations en attente pour badge menu
    validation_count = 0
    if hasattr(request.user, 'profile'):
        role = request.user.profile.role
        if role == 'manager':
            validation_count = LeaveRequest.objects.filter(status='pending', user__profile__manager=request.user, manager_validated=False).count()
            validation_count += TeleworkRequest.objects.filter(status='pending', user__profile__manager=request.user, manager_validated=False).count()
        elif role == 'rh':
            validation_count = LeaveRequest.objects.filter(status='pending', manager_validated=True, rh_validated=False).count()
        elif role == 'admin':
            validation_count = LeaveRequest.objects.filter(status='pending', manager_validated=False).count()
            validation_count += LeaveRequest.objects.filter(status='pending', manager_validated=True, rh_validated=False).count()
            validation_count += TeleworkRequest.objects.filter(status='pending', manager_validated=False).count()
    return render(request, 'extranet/user_admin.html', {
        'users': users,
        'user_balances': user_balances,
        'validation_count': validation_count,
    })

@login_required
def validation(request):
    user = request.user
    type = request.GET.get('type', 'leave')
    leaves = teleworks = []
    if hasattr(user, 'profile'):
        role = user.profile.role
        # Si l'utilisateur est à la fois manager et RH, il doit voir toutes les demandes à valider pour les deux rôles
        is_manager = role in ['manager', 'admin']
        is_rh = role in ['rh', 'admin']
        if is_manager and is_rh:
            leaves = LeaveRequest.objects.filter(status='pending').distinct()
            teleworks = TeleworkRequest.objects.filter(status='pending').distinct()
        elif is_manager:
            leaves = LeaveRequest.objects.filter(status='pending', user__profile__manager=user)
            teleworks = TeleworkRequest.objects.filter(status='pending', user__profile__manager=user)
        elif is_rh:
            leaves = LeaveRequest.objects.filter(status='pending', manager_validated=True)
            teleworks = []
    # Traitement POST pour validation/rejet
    if request.method == 'POST':
        if 'leave_id' in request.POST:
            leave = LeaveRequest.objects.get(id=request.POST['leave_id'])
            action = request.POST.get('action')
            # Affiche les deux boutons si l'utilisateur a les deux rôles
            if action == 'manager_approve' and (user.profile.role == 'manager' or user.profile.role == 'admin') and not leave.manager_validated:
                leave.manager_validated = True
                leave.save()
                messages.success(request, "Demande validée par le manager.")
            elif action == 'rh_approve' and (user.profile.role == 'rh' or user.profile.role == 'admin') and leave.manager_validated and not leave.rh_validated:
                leave.rh_validated = True
                leave.status = 'approved'
                leave.save()
                messages.success(request, "Demande validée par le RH.")
            elif action == 'reject':
                leave.status = 'rejected'
                leave.save()
                messages.error(request, "Demande rejetée.")
            return redirect('extranet:validation')
        elif 'tw_id' in request.POST:
            tw = TeleworkRequest.objects.get(id=request.POST['tw_id'])
            action = request.POST.get('action')
            if action == 'manager_approve' and (user.profile.role == 'manager' or user.profile.role == 'admin') and not tw.manager_validated:
                tw.manager_validated = True
                tw.status = 'approved'
                tw.save()
                messages.success(request, "Télétravail validé.")
            elif action == 'reject':
                tw.status = 'rejected'
                tw.save()
                messages.error(request, "Demande de télétravail rejetée.")
            return redirect(f"{request.path}?type=telework")
    # Calcul du nombre de validations en attente pour badge menu
    validation_count = 0
    if hasattr(request.user, 'profile'):
        role = request.user.profile.role
        if role == 'manager':
            validation_count = LeaveRequest.objects.filter(status='pending', user__profile__manager=request.user, manager_validated=False).count()
            validation_count += TeleworkRequest.objects.filter(status='pending', user__profile__manager=request.user, manager_validated=False).count()
        elif role == 'rh':
            validation_count = LeaveRequest.objects.filter(status='pending', manager_validated=True, rh_validated=False).count()
        elif role == 'admin':
            validation_count = LeaveRequest.objects.filter(status='pending', manager_validated=False).count()
            validation_count += LeaveRequest.objects.filter(status='pending', manager_validated=True, rh_validated=False).count()
            validation_count += TeleworkRequest.objects.filter(status='pending', manager_validated=False).count()
    return render(request, 'extranet/validation.html', {
        'type': type,
        'leaves': leaves if type == 'leave' else [],
        'teleworks': teleworks if type == 'telework' else [],
        'validation_count': validation_count,
    })

# Vue d'administration des congés
@login_required
def admin_leaves(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('extranet:leave_list')
    leaves = LeaveRequest.objects.select_related('user').all().order_by('-start_date')
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="conges_ictgroup.csv"'
        writer = csv.writer(response)
        writer.writerow(['Utilisateur', 'Début', 'Fin', 'Demi-journée', 'Statut', 'Manager', 'RH'])
        for leave in leaves:
            profile = getattr(leave.user, 'profile', None)
            demi = '0.5' if leave.demi_jour != 'full' and leave.start_date == leave.end_date else str((leave.end_date - leave.start_date).days + 1)
            writer.writerow([
                leave.user.username,
                leave.start_date,
                leave.end_date,
                demi,
                leave.get_status_display(),
                profile.manager.get_full_name() if profile and profile.manager else '',
                profile.rh.get_full_name() if profile and profile.rh else '',
            ])
        return response
    # Modification/suppression
    if request.method == 'POST':
        if 'delete_leave' in request.POST:
            leave = LeaveRequest.objects.get(id=request.POST['leave_id'])
            leave.delete()
            messages.success(request, "Demande supprimée.")
            return redirect('extranet:admin_leaves')
        elif 'edit_leave' in request.POST:
            leave = LeaveRequest.objects.get(id=request.POST['leave_id'])
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = request.POST.get('status')
            # Validation des dates
            if not start_date or not end_date:
                messages.error(request, "Merci de renseigner une date de début et de fin au format AAAA-MM-JJ.")
                return redirect(f'{request.path}?edit={leave.id}')
            try:
                leave.start_date = start_date
                leave.end_date = end_date
                leave.status = status
                leave.save()
                messages.success(request, "Demande modifiée.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification : {e}")
                return redirect(f'{request.path}?edit={leave.id}')
            return redirect('extranet:admin_leaves')
    return render(request, 'extranet/admin_leaves.html', {'leaves': leaves})

@require_POST
@login_required
def cancel_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id, user=request.user, status='pending')
    leave.status = 'cancelled'
    leave.save()
    messages.success(request, "Votre demande de congé a été annulée.")
    return redirect('extranet:leave_list')

# Vue d'administration : récapitulatif mensuel
@login_required
def admin_monthly_report(request):
    """Affiche le récapitulatif mensuel de tous les utilisateurs (présence, télétravail, congés, solde) + export CSV."""
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    users = User.objects.all().select_related('profile')
    # Préparation des données pour chaque utilisateur
    user_data = []
    for user in users:
        profile = getattr(user, 'profile', None)
        # Jours de télétravail
        teleworks = TeleworkRequest.objects.filter(user=user, start_date__year=year, start_date__month=month, status='approved')
        days_telework = sum((tw.end_date - tw.start_date).days + 1 for tw in teleworks)
        # Jours de congé
        leaves = LeaveRequest.objects.filter(user=user, start_date__year=year, start_date__month=month, status='approved')
        # Correction demi-journée
        days_leave = sum([0.5 if lv.demi_jour != 'full' and lv.start_date == lv.end_date else (lv.end_date - lv.start_date).days + 1 for lv in leaves])
        # Jours au bureau = jours ouvrés - congés - télétravail
        cal = calendar.Calendar(firstweekday=0)
        cal_days = [d for d in cal.itermonthdates(year, month) if d.month == month]
        cal_fr = France()
        holidays = set(dt for dt, _ in cal_fr.holidays(year))
        workdays = [d for d in cal_days if d.weekday() < 5 and d not in holidays]
        leave_days = set()
        for lv in leaves:
            for n in range((lv.end_date - lv.start_date).days + 1):
                leave_days.add(lv.start_date + timedelta(days=n))
        telework_days = set()
        for tw in teleworks:
            for n in range((tw.end_date - tw.start_date).days + 1):
                telework_days.add(tw.start_date + timedelta(days=n))
        days_at_office = sum(1 for d in workdays if d not in leave_days and d not in telework_days)
        leave_balance = get_leave_balance(user)
        user_data.append({
            'username': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'profile': profile,
            'days_at_office': days_at_office,
            'days_telework': days_telework,
            'days_leave': days_leave,
            'leave_balance': leave_balance.get('balance', 0) if leave_balance else 0,
        })
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="recapitulatif_{year}_{month:02d}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Login', 'Nom', 'Prénom', 'Site', 'Jours bureau', 'Télétravail', 'Congés', 'Solde restant'])
        for u in user_data:
            writer.writerow([
                u['username'],
                u['last_name'],
                u['first_name'],
                getattr(u['profile'], 'site', ''),
                u['days_at_office'],
                u['days_telework'],
                u['days_leave'],
                u['leave_balance'],
            ])
        return response
    # Pour le template
    selected_month = f"{year:04d}-{month:02d}"
    year_range = list(range(today.year-1, today.year+2))
    month_range = list(range(1, 13))
    return render(request, 'extranet/admin_monthly_report.html', {
        'users': user_data,
        'selected_month': selected_month,
        'year_range': year_range,
        'month_range': month_range,
    })

# Vue d'administration des télétravails
@login_required
def admin_teleworks(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('extranet:telework_list')
    teleworks = TeleworkRequest.objects.select_related('user').all().order_by('-start_date')
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teletravail_ictgroup.csv"'
        writer = csv.writer(response)
        writer.writerow(['Utilisateur', 'Début', 'Fin', 'Statut', 'Manager', 'RH'])
        for tw in teleworks:
            profile = getattr(tw.user, 'profile', None)
            writer.writerow([
                tw.user.username,
                tw.start_date,
                tw.end_date,
                tw.status,
                profile.manager.get_full_name() if profile and profile.manager else '',
                profile.rh.get_full_name() if profile and profile.rh else '',
            ])
        return response
    # Suppression
    if request.method == 'POST':
        if 'delete_telework' in request.POST:
            tw = TeleworkRequest.objects.get(id=request.POST['telework_id'])
            tw.delete()
            messages.success(request, "Demande supprimée.")
            return redirect('extranet:admin_teleworks')
    return render(request, 'extranet/admin_teleworks.html', {'teleworks': teleworks})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import StockItem, StockMovement
from django.contrib import messages

@login_required
def stock_view(request):
    if request.method == 'POST':
        if not request.user.is_superuser and not request.user.profile.role == 'manager':
            messages.error(request, "Accès réservé à l'administrateur et au manager.")
            return redirect('extranet:stock')

        action = request.POST.get('action')
        if action == 'create':
            code = request.POST.get('code')
            designation = request.POST.get('designation')
            fournisseur = request.POST.get('fournisseur')
            type = request.POST.get('type')
            quantity = int(request.POST.get('quantity', 0))
            remarks = request.POST.get('remarks', '')

            StockItem.objects.create(
                code=code,
                designation=designation,
                fournisseur=fournisseur,
                type=type,
                quantity=quantity,
                remarks=remarks
            )
            messages.success(request, "Article créé avec succès.")

        elif action == 'update':
            stock_item_id = request.POST.get('stock_item_id')
            stock_item = get_object_or_404(StockItem, id=stock_item_id)
            stock_item.designation = request.POST.get('designation')
            stock_item.fournisseur = request.POST.get('fournisseur')
            stock_item.type = request.POST.get('type')
            stock_item.quantity = int(request.POST.get('quantity', 0))
            stock_item.remarks = request.POST.get('remarks', '')
            stock_item.save()
            messages.success(request, "Article mis à jour avec succès.")

        elif action == 'delete':
            stock_item_id = request.POST.get('stock_item_id')
            stock_item = get_object_or_404(StockItem, id=stock_item_id)
            stock_item.delete()
            messages.success(request, "Article supprimé avec succès.")

        return redirect('extranet:stock')

    stock_items = StockItem.objects.all()
    return render(request, 'extranet/stock.html', {'stock_items': stock_items})

@login_required
def entry_exit_view(request):
    if request.method == 'POST':
        stock_item_id = request.POST.get('stock_item')
        movement_type = request.POST.get('movement_type')
        quantity = int(request.POST.get('quantity'))
        remarks = request.POST.get('remarks', '')

        stock_item = StockItem.objects.get(id=stock_item_id)
        if movement_type == 'entry':
            stock_item.quantity += quantity
        elif movement_type == 'exit':
            if stock_item.quantity < quantity:
                messages.error(request, "Quantité insuffisante en stock.")
                return redirect('extranet:entry_exit')
            stock_item.quantity -= quantity
        stock_item.save()

        StockMovement.objects.create(
            stock_item=stock_item,
            user=request.user,
            movement_type=movement_type,
            quantity=quantity,
            remarks=remarks
        )
        messages.success(request, "Mouvement enregistré avec succès.")
        return redirect('extranet:entry_exit')

    stock_items = StockItem.objects.all()
    return render(request, 'extranet/entry_exit.html', {'stock_items': stock_items})

@login_required
def movements_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel':
            movement_id = request.POST.get('movement_id')
            movement = get_object_or_404(StockMovement, id=movement_id)

            # Check permissions
            if not request.user.is_superuser and not request.user.profile.role == 'manager':
                if movement.user != request.user:
                    messages.error(request, "Vous n'avez pas la permission d'annuler cette transaction.")
                    return redirect('extranet:movements')

            # Reverse the stock movement
            stock_item = movement.stock_item
            if movement.movement_type == 'entry':
                stock_item.quantity -= movement.quantity
            elif movement.movement_type == 'exit':
                stock_item.quantity += movement.quantity
            stock_item.save()

            # Delete the movement
            movement.delete()
            messages.success(request, "Transaction annulée avec succès.")

        return redirect('extranet:movements')

    movements = StockMovement.objects.select_related('stock_item', 'user').order_by('-date')
    return render(request, 'extranet/movements.html', {'movements': movements})