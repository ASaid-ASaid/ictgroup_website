# =====================
# Modèles principaux de l'app 'extranet'
# Chaque classe correspond à une table de la base de données.
# Les modèles gèrent la logique métier et les relations entre les entités.
# =====================
from datetime import date, timedelta

from django import template
from django.contrib.auth.models import User
from django.db import models
from workalendar.europe import France

# =====================
# Modèles principaux
# =====================


class LeaveRequest(models.Model):
    """
    Modèle représentant une demande de congé.
    - Gère le workflow de validation multi-acteurs (manager, RH, admin).
    - Statuts : en attente, approuvée, rejetée, annulée.
    - Calcul automatique des dates et suivi de l'utilisateur demandeur.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="leave_requests"
    )  # L'utilisateur qui fait la demande
    start_date = models.DateField()  # Date de début du congé
    end_date = models.DateField()  # Date de fin du congé
    reason = models.TextField(blank=True, null=True)  # Raison optionnelle
    submitted_at = models.DateTimeField(auto_now_add=True)  # Date de soumission

    # Statuts possibles pour la demande
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
        ("cancelled", "Annulée"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Statut de la demande (workflow de validation)",
    )
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification

    # Champs de validation multi-acteurs
    manager_validated = models.BooleanField(
        default=False, help_text="Validation du manager"
    )
    rh_validated = models.BooleanField(default=False, help_text="Validation RH")
    admin_validated = models.BooleanField(default=False, help_text="Validation admin")

    DEMI_JOUR_CHOICES = [
        ("full", "Journée complète"),
        ("am", "Matin"),
        ("pm", "Après-midi"),
    ]
    demi_jour = models.CharField(
        max_length=4,
        choices=DEMI_JOUR_CHOICES,
        default="full",
        help_text="Demi-journée ou journée complète",
    )

    def __str__(self):
        # Représentation lisible de la demande
        return f"Demande de congé de {self.user.username} du {self.start_date} au {self.end_date} ({self.status})"

    class Meta:
        ordering = ["-submitted_at"]  # Trie par date de soumission décroissante

    @property
    def get_nb_days(self):
        """
        Retourne 0.5 si demi-journée (am/pm), sinon le nombre de jours calendaires entre start_date et end_date inclus.
        """
        if self.demi_jour in ["am", "pm"]:
            return 0.5
        return (self.end_date - self.start_date).days + 1


class TeleworkRequest(models.Model):
    """
    Modèle pour la demande de télétravail.
    - Gère les plages de dates.
    - Statuts et validation manager.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="telework_requests"
    )
    start_date = models.DateField()  # Date de début du télétravail
    end_date = models.DateField()  # Date de fin du télétravail
    reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
        ("cancelled", "Annulée"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Statut de la demande",
    )
    updated_at = models.DateTimeField(auto_now=True)
    manager_validated = models.BooleanField(
        default=False, help_text="Validation du manager"
    )

    def __str__(self):
        if self.start_date == self.end_date:
            return (
                f"Télétravail {self.user.username} le {self.start_date} ({self.status})"
            )
        return f"Télétravail {self.user.username} du {self.start_date} au {self.end_date} ({self.status})"

    class Meta:
        ordering = ["-start_date"]


# Profil utilisateur pour gérer les rôles et rattachements
class UserProfile(models.Model):
    SITE_CHOICES = [
        ("tunisie", "Tunisie"),
        ("france", "France"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "Utilisateur"),
            ("manager", "Manager"),
            ("rh", "RH"),
            ("admin", "Admin"),
        ],
        default="user",
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_users",
    )
    rh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rh_users",
    )
    site = models.CharField(max_length=10, choices=SITE_CHOICES, default="tunisie")
    carry_over = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0.0,
        help_text="Report manuel de congés de l'année précédente",
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


def get_leave_balance(user):
    """
    Version optimisée avec cache pour le calcul de solde de congés.
    Utilise le système de cache pour éviter les recalculs répétitifs.
    """
    from .cache_managers import OptimizedLeaveManager

    # Utiliser le gestionnaire optimisé avec cache
    return OptimizedLeaveManager.get_or_calculate_balance(user)


def get_leave_balance_detailed(user):
    """
    Calcule le solde de congés pour un utilisateur selon les nouvelles règles :
    - Période de référence : 1er juin N-1 au 31 mai N
    - Tunisie : 1.8 jours/mois, jours ouvrés seulement
    - France : 2.5 jours/mois, jours ouvrables (vendredi seul = vendredi + samedi)
    Version détaillée sans cache pour les besoins spécifiques.
    """
    today = date.today()

    # Période de référence : 1er juin de l'année précédente au 31 mai de l'année en cours
    if today.month >= 6:  # juin à décembre
        period_start = date(today.year, 6, 1)
        period_end = date(today.year + 1, 5, 31)
        current_period_year = today.year
    else:  # janvier à mai
        period_start = date(today.year - 1, 6, 1)
        period_end = date(today.year, 5, 31)
        current_period_year = today.year - 1

    # Date d'embauche
    date_joined = (
        user.date_joined.date() if hasattr(user, "date_joined") else period_start
    )

    # Début effectif de travail dans la période
    work_start = max(period_start, date_joined)
    work_end = min(period_end, today)

    # Récupère le site (Tunisie/France)
    site = (
        getattr(user.profile, "site", "tunisie").lower()
        if hasattr(user, "profile")
        else "tunisie"
    )

    # Calcul des mois travaillés dans la période de référence
    if work_start <= work_end:
        months_worked = (
            (work_end.year - work_start.year) * 12
            + work_end.month
            - work_start.month
            + 1
        )
    else:
        months_worked = 0

    # Jours acquis selon le site
    days_per_month = 2.5 if site == "france" else 1.8
    days_acquired = round(max(0, months_worked * days_per_month), 1)

    # Fonction pour calculer les jours de congé selon les règles du site
    def calculate_leave_days(leave):
        if leave.demi_jour != "full" and leave.start_date == leave.end_date:
            return 0.5

        # Pour la France : règle des jours ouvrables
        if site == "france":
            leave_dates = []
            current_date = leave.start_date
            while current_date <= leave.end_date:
                leave_dates.append(current_date)
                current_date += timedelta(days=1)

            # Calcul spécial pour la France
            total_days = 0
            cal_fr = France()
            holidays = set(dt for dt, _ in cal_fr.holidays(leave.start_date.year))

            for leave_date in leave_dates:
                total_days += 1
                # Si c'est un vendredi et que le samedi n'est pas déjà dans la période de congé
                if (
                    leave_date.weekday() == 4  # vendredi
                    and leave_date + timedelta(days=1) not in leave_dates
                ):
                    total_days += 1  # ajouter le samedi
                # Si c'est un jeudi et que le vendredi est férié et samedi pas dans congé
                elif (
                    leave_date.weekday() == 3  # jeudi
                    and leave_date + timedelta(days=1) in holidays  # vendredi férié
                    and leave_date + timedelta(days=2) not in leave_dates
                ):  # samedi pas en congé
                    total_days += 1  # ajouter le samedi

            return total_days
        else:
            # Pour la Tunisie : jours ouvrés seulement (lundi-vendredi)
            total_days = 0
            current_date = leave.start_date
            while current_date <= leave.end_date:
                if current_date.weekday() < 5:  # lundi à vendredi seulement
                    total_days += 1
                current_date += timedelta(days=1)
            return total_days

    # Jours pris dans la période de référence actuelle
    leaves_current = user.leave_requests.filter(
        status="approved", start_date__gte=period_start, start_date__lte=period_end
    )
    days_taken = sum([calculate_leave_days(leave) for leave in leaves_current])

    # Report de la période précédente (manuel si défini, sinon calculé)
    if hasattr(user, "profile") and user.profile.carry_over > 0:
        report = float(user.profile.carry_over)
    else:
        prev_period_start = date(current_period_year - 1, 6, 1)
        prev_period_end = date(current_period_year, 5, 31)

        # Calcul des congés de la période précédente
        prev_work_start = max(prev_period_start, date_joined)
        prev_work_end = min(prev_period_end, date(current_period_year, 5, 31))

        if prev_work_start <= prev_work_end:
            prev_months_worked = (
                (prev_work_end.year - prev_work_start.year) * 12
                + prev_work_end.month
                - prev_work_start.month
                + 1
            )
            prev_days_acquired = round(max(0, prev_months_worked * days_per_month), 1)

            # Congés pris dans la période précédente
            prev_leaves = user.leave_requests.filter(
                status="approved",
                start_date__gte=prev_period_start,
                start_date__lte=prev_period_end,
            )
            prev_days_taken = sum(
                [calculate_leave_days(leave) for leave in prev_leaves]
            )
            report = max(0, round(prev_days_acquired - prev_days_taken, 1))
        else:
            report = 0

    # Jours à prendre avant le 30 avril (fin de période de report)
    must_take_before_april = report if today <= date(today.year, 4, 30) else 0

    # Solde restant
    balance = round(days_acquired + report - days_taken, 1)

    return {
        "acquired": days_acquired,
        "taken": days_taken,
        "balance": balance,
        "report": report,
        "must_take_before_april": must_take_before_april,
        "site": site,
        "period_start": period_start,
        "period_end": period_end,
    }


class StockItem(models.Model):
    code = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=255)
    fournisseur = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.designation}"


class StockMovement(models.Model):
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movement_type = models.CharField(
        max_length=10, choices=[("entry", "Entrée"), ("exit", "Sortie")]
    )
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.movement_type} - {self.stock_item.code} by {self.user.username}"


# =====================
# Modèles de cache pour optimiser les performances
# =====================


class UserLeaveBalanceCache(models.Model):
    """
    Cache des soldes de congés par utilisateur et par année.
    Évite les recalculs répétitifs des soldes (acquis, pris, report, restant).
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="leave_balance_cache"
    )
    year = models.IntegerField()
    acquired_days = models.DecimalField(
        max_digits=4, decimal_places=1, default=0, help_text="Jours acquis dans l'année"
    )
    taken_days = models.DecimalField(
        max_digits=4, decimal_places=1, default=0, help_text="Jours pris dans l'année"
    )
    carry_over_days = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Report de l'année précédente",
    )
    remaining_days = models.DecimalField(
        max_digits=4, decimal_places=1, default=0, help_text="Solde restant"
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "year")
        indexes = [
            models.Index(fields=["user", "year"], name="idx_balance_user_year"),
            models.Index(fields=["last_updated"], name="idx_balance_updated"),
        ]
        verbose_name = "Cache solde congés"
        verbose_name_plural = "Cache soldes congés"

    def __str__(self):
        return f"{self.user.username} - {self.year} (Restant: {self.remaining_days}j)"


class UserMonthlyReportCache(models.Model):
    """
    Cache des rapports mensuels par utilisateur.
    Stocke les calculs de jours au bureau, télétravail, congés pour éviter les recalculs.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="monthly_report_cache"
    )
    year = models.IntegerField()
    month = models.IntegerField()
    days_at_office = models.IntegerField(
        default=0, help_text="Jours travaillés au bureau"
    )
    days_telework = models.IntegerField(default=0, help_text="Jours en télétravail")
    days_leave = models.DecimalField(
        max_digits=4, decimal_places=1, default=0, help_text="Jours de congés pris"
    )
    total_workdays = models.IntegerField(
        default=0, help_text="Total jours ouvrés du mois"
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "year", "month")
        indexes = [
            models.Index(
                fields=["user", "year", "month"], name="idx_monthly_user_period"
            ),
            models.Index(fields=["last_updated"], name="idx_monthly_updated"),
        ]
        verbose_name = "Cache rapport mensuel"
        verbose_name_plural = "Cache rapports mensuels"

    def __str__(self):
        return f"{self.user.username} - {self.year}/{self.month:02d} (Bureau: {self.days_at_office}j, TT: {self.days_telework}j)"


register = template.Library()


@register.filter
def get_nb_days(leave):
    """
    Retourne 0.5 si demi-journée (am/pm), sinon le nombre de jours calendaires entre start_date et end_date inclus.
    """
    if leave.demi_jour in ["am", "pm"]:
        return 0.5
    return (leave.end_date - leave.start_date).days + 1
