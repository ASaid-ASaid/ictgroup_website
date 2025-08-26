"""
Vues du calendrier de présence.
"""

import calendar
import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

# django.utils.timezone not used in this module
from workalendar.europe import France

from ..models import LeaveRequest, TeleworkRequest, get_leave_balance

logger = logging.getLogger(__name__)


@login_required
def calendar_view(request):
    """
    Affiche le calendrier mensuel de présence.

    Montre congés, télétravail, fériés, week-ends et jours au bureau pour un
    utilisateur ou en mode global (pour les admins/managers).
    """
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
    if can_see_global and (mode == "global" and users or user.is_superuser):
        leaves = LeaveRequest.objects.filter(
            user=selected_user,
            start_date__year=year,
            start_date__month=month,
            status="approved",
        )
        teleworks = TeleworkRequest.objects.filter(
            user=selected_user,
            start_date__year=year,
            start_date__month=month,
            status="approved",
        )
    else:
        leaves = LeaveRequest.objects.filter(
            user=user,
            start_date__year=year,
            start_date__month=month,
            status="approved",
        )
        teleworks = TeleworkRequest.objects.filter(
            user=user,
            start_date__year=year,
            start_date__month=month,
            status="approved",
        )
    leave_days = set()
    demi_jour_days = {}
    for leave in leaves:
        if leave.demi_jour != "full" and leave.start_date == leave.end_date:
            demi_jour_days[leave.start_date] = leave.demi_jour
            # Pour les demi-journées, on ne les compte pas comme des jours complets
            # de congé pour le calcul des jours au bureau
        else:
            for n in range((leave.end_date - leave.start_date).days + 1):
                leave_days.add(leave.start_date + timedelta(days=n))
    # Jours de télétravail (jours ouvrés uniquement)
    telework_days = set()
    for tw in teleworks:
        current_date = tw.start_date
        while current_date <= tw.end_date:
            if current_date.weekday() < 5:  # 0-4 = Lundi-Vendredi
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
    workdays = [
        d
        for d in cal_days
        if d.month == month and d.weekday() < 5 and d not in holidays
    ]
    days_at_office = 0
    for d in workdays:
        if d <= today:
            if d in demi_jour_days:
                # Demi-journée : considéré comme jour hors bureau (0 jour au bureau)
                pass  # N'ajoute rien, donc 0 jour au bureau
            elif d not in leave_days and d not in telework_days:
                # Jour normal : on ajoute 1 jour au bureau
                days_at_office += 1
            # Si congé complet ou télétravail : on n'ajoute rien (0 jour au bureau)
    holidays_count = sum(1 for d in cal_days if d.month == month and d in holidays)
    # Pour les congés, il faut compter les demi-journées comme 0.5
    leaves_count = 0
    for d in cal_days:
        if d.month == month:
            if d in demi_jour_days:
                leaves_count += 0.5
            elif d in leave_days:
                leaves_count += 1
    telework_count = sum(1 for d in cal_days if d.month == month and d in telework_days)
    weekends_count = sum(1 for d in cal_days if d.month == month and d.weekday() >= 5)
    # selected_month pour compatibilité template
    selected_month = f"{year:04d}-{month:02d}"

    # Ajout du solde de congés pour l'utilisateur sélectionné
    leave_balance_info = get_leave_balance(selected_user)

    return render(
        request,
        "extranet/calendar.html",
        {
            "calendar": weeks,
            "selected_month": selected_month,
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
        },
    )


# Alias pour compatibilité avec l'ancien nom
presence_calendar = calendar_view


@login_required
def calendar_api(request):
    """API pour récupérer les événements du calendrier en AJAX."""

    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))

    # Utilisation de la logique du calendar_view pour la cohérence
    user = request.user

    # Récupération des congés
    leaves = LeaveRequest.objects.filter(
        user=user,
        start_date__year=year,
        start_date__month=month,
        status="approved",
    )

    # Récupération du télétravail
    teleworks = TeleworkRequest.objects.filter(
        user=user,
        start_date__year=year,
        start_date__month=month,
        status="approved",
    )

    events = []

    # Ajout des événements de congés
    for leave in leaves:
        current_date = leave.start_date
        while current_date <= leave.end_date:
            events.append(
                {
                    "date": current_date.isoformat(),
                    "type": "leave",
                    "title": "Congé",
                    "description": leave.reason or "Congé",
                }
            )
            current_date += timedelta(days=1)

    # Ajout des événements de télétravail (jours ouvrés uniquement)
    for telework in teleworks:
        current_date = telework.start_date
        while current_date <= telework.end_date:
            if current_date.weekday() < 5:  # 0-4 = Lundi-Vendredi
                events.append(
                    {
                        "date": current_date.isoformat(),
                        "type": "telework",
                        "title": "Télétravail",
                        "description": telework.reason or "Télétravail",
                    }
                )
            current_date += timedelta(days=1)

    return JsonResponse({"events": events})
