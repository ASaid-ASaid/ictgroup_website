"""
Vues du calendrier de présence.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, timedelta, datetime
from workalendar.europe import France
import calendar
import logging
import csv

from ..models import LeaveRequest, TeleworkRequest, get_leave_balance

logger = logging.getLogger(__name__)


@login_required
def calendar_view(request):
    """Affiche le calendrier mensuel de présence (congés, télétravail, fériés, week-ends, jours au bureau)."""
    user = request.user
    today = date.today()
    # Mode global si superuser/admin/manager/rh et paramètre global présent
    mode = request.GET.get("mode", "me")
    user_id = request.GET.get("user_id")
    selected_user = user
    users = None
    can_see_global = user.is_superuser or (
        hasattr(user, "profile")
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )
    if mode == "global" and can_see_global:
        users = User.objects.all().order_by("last_name", "first_name")
        if user_id:
            try:
                selected_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                selected_user = user
    # Récupère séparément mois et année depuis les menus déroulants
    month = request.GET.get("month")
    year = request.GET.get("year")
    if month and year:
        year = int(year)
        month = int(month)
    else:
        year, month = today.year, today.month
    # Pour le selecteur de mois/année
    year_range = list(range(today.year - 1, today.year + 2))
    month_range = list(range(1, 13))
    cal = calendar.Calendar(firstweekday=0)  # Lundi
    cal_days = list(cal.itermonthdates(year, month))
    cal_fr = France()
    holidays = set(dt for dt, _ in cal_fr.holidays(year))
    # Dates de début et fin du mois pour un filtrage plus précis
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    if can_see_global and (mode == "global" and users or user.is_superuser):
        # Filtrage plus précis : demandes qui chevauchent avec le mois affiché
        leaves = LeaveRequest.objects.filter(
            user=selected_user,
            start_date__lte=last_day,
            end_date__gte=first_day,
            status="approved",
        )
        teleworks = TeleworkRequest.objects.filter(
            user=selected_user,
            start_date__lte=last_day,
            end_date__gte=first_day,
            status="approved",
        )
    else:
        # Filtrage plus précis : demandes qui chevauchent avec le mois affiché
        leaves = LeaveRequest.objects.filter(
            user=user,
            start_date__lte=last_day,
            end_date__gte=first_day,
            status="approved",
        )
        teleworks = TeleworkRequest.objects.filter(
            user=user,
            start_date__lte=last_day,
            end_date__gte=first_day,
            status="approved",
        )
    leave_days = set()
    demi_jour_days = {}
    for leave in leaves:
        current_date = leave.start_date
        while current_date <= leave.end_date:
            # Ne traiter que les jours du mois affiché
            if current_date.month == month and current_date.year == year:
                if leave.demi_jour != "full" and leave.start_date == leave.end_date:
                    demi_jour_days[current_date] = leave.demi_jour
                else:
                    leave_days.add(current_date)
            current_date += timedelta(days=1)
    # Jours de télétravail (jours ouvrés uniquement)
    telework_days = set()
    for tw in teleworks:
        current_date = tw.start_date
        while current_date <= tw.end_date:
            # Ne traiter que les jours du mois affiché et les jours ouvrés
            if (current_date.month == month and current_date.year == year and 
                current_date.weekday() < 5):  # 0-4 = Lundi-Vendredi
                telework_days.add(current_date)
            current_date += timedelta(days=1)
    weeks = []
    week = []
    for d in cal_days:
        if d.month != month:
            week.append(None)
        else:
            day_info = {
                "day": d.day,
                "is_today": d == today and selected_user == user,
                "is_holiday": d in holidays,
                "is_leave": d in leave_days,
                "is_telework": d in telework_days,
                "is_weekend": d.weekday() >= 5,
                "demi_jour": demi_jour_days.get(d, None),
            }
            week.append(day_info)
        if len(week) == 7:
            weeks.append(week)
            week = []
    # Calcul des jours au bureau (plus précis)
    workdays = [
        d
        for d in cal_days
        if d.month == month and d.weekday() < 5 and d not in holidays
    ]
    days_at_office = 0
    for d in workdays:
        if d <= today:  # Seulement les jours passés et aujourd'hui
            if d in demi_jour_days:
                # Demi-journée : compter 0.5 jour au bureau si c'est matin + après-midi au bureau
                # ou 0 si c'est toute la journée en congé
                if d not in telework_days:  # Si pas de télétravail le même jour
                    days_at_office += 0.5
            elif d not in leave_days and d not in telework_days:
                # Jour normal au bureau
                days_at_office += 1
            # Si congé complet ou télétravail : 0 jour au bureau
    # Statistiques plus précises
    holidays_count = sum(
        1 for d in cal_days if d.month == month and d in holidays
    )
    
    # Calcul précis des jours de congé avec demi-journées
    leaves_count = 0
    for d in cal_days:
        if d.month == month:
            if d in demi_jour_days:
                leaves_count += 0.5
            elif d in leave_days:
                leaves_count += 1
                
    # Télétravail uniquement pour les jours ouvrés du mois
    telework_count = sum(
        1 for d in cal_days 
        if d.month == month and d in telework_days and d.weekday() < 5
    )
    
    # Week-ends du mois
    weekends_count = sum(
        1 for d in cal_days if d.month == month and d.weekday() >= 5
    )
    # selected_month pour compatibilité template
    selected_month = date(year, month, 1)
    
    # Navigation mois précédent/suivant
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)
    
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    # Ajout du solde de congés pour l'utilisateur sélectionné
    leave_balance_info = get_leave_balance(selected_user)
    
    # Calcul des métriques de performance
    total_workdays_in_month = len([d for d in cal_days if d.month == month and d.weekday() < 5 and d not in holidays])
    workdays_passed = len([d for d in cal_days if d.month == month and d.weekday() < 5 and d not in holidays and d <= today])
    
    # Pourcentage de présence au bureau (pour les jours passés)
    presence_percentage = 0
    if workdays_passed > 0:
        presence_percentage = round((days_at_office / workdays_passed) * 100, 1)
    
    # Statut de présence
    presence_status = "excellent"  # > 80%
    if presence_percentage < 50:
        presence_status = "faible"
    elif presence_percentage < 70:
        presence_status = "moyen"
    elif presence_percentage < 80:
        presence_status = "bon"
    
    return render(
        request,
        "extranet/calendar.html",
        {
            "calendar": weeks,
            "selected_month": selected_month,
            "prev_month": prev_month,
            "next_month": next_month,
            "current_year": year,
            "current_month": month,
            "days_at_office": days_at_office,
            "holidays_count": holidays_count,
            "leaves_count": leaves_count,
            "telework_count": telework_count,
            "weekends_count": weekends_count,
            "year_range": year_range,
            "month_range": month_range,
            "mode": mode,
            "users": users,
            "selected_user": selected_user,
            "can_see_global": can_see_global,
            "leave_balance": leave_balance_info,
            "total_workdays_in_month": total_workdays_in_month,
            "workdays_passed": workdays_passed,
            "presence_percentage": presence_percentage,
            "presence_status": presence_status,
        },
    )


# Alias pour compatibilité avec l'ancien nom
presence_calendar = calendar_view


@login_required
def calendar_api(request):
    """API pour récupérer les événements du calendrier en AJAX."""
    
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Utilisation de la même logique que calendar_view pour la cohérence
    user = request.user
    
    # Dates de début et fin du mois pour un filtrage précis
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Récupération des congés avec filtrage précis
    leaves = LeaveRequest.objects.filter(
        user=user,
        start_date__lte=last_day,
        end_date__gte=first_day,
        status="approved",
    )
    
    # Récupération du télétravail avec filtrage précis
    teleworks = TeleworkRequest.objects.filter(
        user=user,
        start_date__lte=last_day,
        end_date__gte=first_day,
        status="approved",
    )
    
    events = []
    
    # Ajout des événements de congés (avec gestion des demi-journées)
    for leave in leaves:
        current_date = leave.start_date
        while current_date <= leave.end_date:
            # Ne traiter que les jours du mois affiché
            if current_date.month == month and current_date.year == year:
                event_data = {
                    'date': current_date.isoformat(),
                    'type': 'leave',
                    'title': 'Congé',
                    'description': leave.reason or 'Congé',
                }
                # Ajouter l'information demi-journée si applicable
                if leave.demi_jour != "full" and leave.start_date == leave.end_date:
                    event_data['demi_jour'] = leave.demi_jour
                    event_data['title'] = f'Congé {"matin" if leave.demi_jour == "am" else "après-midi"}'
                
                events.append(event_data)
            current_date += timedelta(days=1)
    
    # Ajout des événements de télétravail (jours ouvrés uniquement)
    for telework in teleworks:
        current_date = telework.start_date
        while current_date <= telework.end_date:
            # Ne traiter que les jours du mois affiché et les jours ouvrés
            if (current_date.month == month and current_date.year == year and 
                current_date.weekday() < 5):  # 0-4 = Lundi-Vendredi
                events.append({
                    'date': current_date.isoformat(),
                    'type': 'telework',
                    'title': 'Télétravail',
                    'description': telework.reason or 'Télétravail',
                })
            current_date += timedelta(days=1)
    
    return JsonResponse({'events': events})


@login_required
def calendar_export_csv(request):
    """Export des données du calendrier en CSV."""
    
    user = request.user
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Mode global si autorisé
    mode = request.GET.get("mode", "me")
    user_id = request.GET.get("user_id")
    selected_user = user
    can_see_global = user.is_superuser or (
        hasattr(user, "profile")
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )
    if mode == "global" and can_see_global and user_id:
        try:
            selected_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            selected_user = user
    
    # Dates de début et fin du mois
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Récupération des données
    leaves = LeaveRequest.objects.filter(
        user=selected_user,
        start_date__lte=last_day,
        end_date__gte=first_day,
        status="approved",
    )
    
    teleworks = TeleworkRequest.objects.filter(
        user=selected_user,
        start_date__lte=last_day,
        end_date__gte=first_day,
        status="approved",
    )
    
    # Préparation du CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="calendrier_{selected_user.username}_{year}_{month:02d}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Jour', 'Type', 'Statut', 'Détails'])
    
    # Génération des données pour chaque jour du mois
    cal = calendar.Calendar(firstweekday=0)
    cal_days = list(cal.itermonthdates(year, month))
    cal_fr = France()
    holidays = dict(cal_fr.holidays(year))
    
    for d in cal_days:
        if d.month != month:
            continue
            
        day_name = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][d.weekday()]
        
        # Déterminer le type de jour
        if d in holidays:
            day_type = "Jour férié"
            status = holidays[d]
            details = ""
        elif d.weekday() >= 5:
            day_type = "Week-end"
            status = "Repos"
            details = ""
        else:
            # Vérifier congés
            is_leave = False
            is_demi_jour = False
            leave_details = ""
            
            for leave in leaves:
                if leave.start_date <= d <= leave.end_date:
                    is_leave = True
                    if leave.demi_jour != "full" and leave.start_date == leave.end_date:
                        is_demi_jour = True
                        leave_details = f"Demi-journée {leave.demi_jour.upper()}: {leave.reason or 'Congé'}"
                    else:
                        leave_details = f"Congé: {leave.reason or 'Congé'}"
                    break
            
            # Vérifier télétravail
            is_telework = False
            telework_details = ""
            
            for telework in teleworks:
                if telework.start_date <= d <= telework.end_date:
                    is_telework = True
                    telework_details = f"Télétravail: {telework.reason or 'Télétravail'}"
                    break
            
            if is_leave:
                day_type = "Demi-journée congé" if is_demi_jour else "Congé"
                status = "Absent"
                details = leave_details
            elif is_telework:
                day_type = "Télétravail"
                status = "Travail à distance"
                details = telework_details
            else:
                day_type = "Jour ouvré"
                status = "Présent au bureau"
                details = ""
        
        writer.writerow([
            d.strftime('%Y-%m-%d'),
            day_name,
            day_type,
            status,
            details
        ])
    
    return response