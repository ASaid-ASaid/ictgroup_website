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
        return "Demande de congé de %s du %s au %s (%s)" % (
            self.user.username,
            self.start_date,
            self.end_date,
            self.status,
        )

    class Meta:
        ordering = ["-submitted_at"]  # Trie par date de soumission décroissante

    @property
    def get_nb_days(self):
        """
        Retourne 0.5 pour demi-journée (am/pm), sinon calcule le nombre de jours
        selon les règles spécifiques au site (France vs Tunisie).
        """
        if self.demi_jour in ["am", "pm"]:
            return 0.5
        
        # Calcul selon le site de l'utilisateur
        if hasattr(self.user, 'profile') and self.user.profile.site == 'france':
            # France : jours ouvrables avec règle spéciale vendredi-samedi
            from datetime import timedelta
            
            total_days = 0
            current_date = self.start_date
            
            while current_date <= self.end_date:
                weekday = current_date.weekday()
                
                if weekday < 5:  # lundi à vendredi
                    total_days += 1
                    
                    # Règle spéciale : si c'est un vendredi, le samedi suivant est automatiquement congé
                    if weekday == 4:  # vendredi
                        saturday = current_date + timedelta(days=1)
                        # Vérifier si le samedi est dans la période OU le vendredi est le dernier jour de la demande
                        if saturday <= self.end_date or current_date == self.end_date:
                            total_days += 1  # ajouter le samedi automatiquement
                            
                elif weekday == 5:  # samedi
                    # Samedi uniquement s'il n'a pas déjà été compté avec un vendredi précédent
                    previous_day = current_date - timedelta(days=1)
                    if previous_day < self.start_date or previous_day.weekday() != 4:
                        total_days += 1
                        
                current_date += timedelta(days=1)
                
            return total_days
        else:
            # Tunisie : jours ouvrés (lundi-vendredi uniquement)
            from datetime import timedelta
            
            total_days = 0
            current_date = self.start_date
            while current_date <= self.end_date:
                if current_date.weekday() < 5:  # lundi à vendredi
                    total_days += 1
                current_date += timedelta(days=1)
            return total_days


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
    rh_validated = models.BooleanField(default=False, help_text="Validation RH")

    def __str__(self):
        if self.start_date == self.end_date:
            return "Télétravail %s le %s (%s)" % (
                self.user.username,
                self.start_date,
                self.status,
            )
        return "Télétravail %s du %s au %s (%s)" % (
            self.user.username,
            self.start_date,
            self.end_date,
            self.status,
        )

    class Meta:
        ordering = ["-start_date"]


class OverTimeRequest(models.Model):
    """
    Modèle pour les demandes d'heures supplémentaires (weekend en télétravail).
    - Gère les heures travaillées durant les weekends
    - Statuts et validation manager/RH
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="overtime_requests"
    )
    work_date = models.DateField(help_text="Date de travail (samedi ou dimanche)")
    hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        help_text="Nombre d'heures travaillées"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Description du travail effectué"
    )
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
    rh_validated = models.BooleanField(default=False, help_text="Validation RH")

    def clean(self):
        """Validation : s'assurer que la date est un weekend"""
        from django.core.exceptions import ValidationError
        if self.work_date and self.work_date.weekday() not in [5, 6]:  # Samedi=5, Dimanche=6
            raise ValidationError("Les heures supplémentaires ne peuvent être déclarées que pour les weekends (samedi/dimanche)")

    def __str__(self):
        return f"Heures supplémentaires {self.user.username} - {self.work_date} ({self.hours}h) - {self.status}"

    class Meta:
        ordering = ["-work_date"]
        unique_together = ("user", "work_date")  # Un seul enregistrement par utilisateur/date


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

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Document(models.Model):
    """
    Modèle pour la gestion des documents.
    - Gère l'upload et le téléchargement de documents OU des liens
    - Permet de définir qui peut accéder aux documents
    - Gestion des catégories de documents
    """
    
    CATEGORY_CHOICES = [
        ("payslip", "Fiche de paie"),
        ("certificate", "Attestation de travail"),
        ("note", "Note générale"),
        ("policy", "Politique d'entreprise"),
        ("form", "Formulaire"),
        ("link", "Lien externe"),
        ("other", "Autre"),
    ]
    
    TARGET_CHOICES = [
        ("all", "Tout le monde"),
        ("specific", "Personnes spécifiques"),
        ("role", "Par rôle"),
    ]

    TYPE_CHOICES = [
        ("file", "Fichier"),
        ("link", "Lien"),
    ]
    
    title = models.CharField(max_length=200, help_text="Titre du document")
    description = models.TextField(blank=True, null=True, help_text="Description du document")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
        help_text="Catégorie du document"
    )
    
    # Type de document : fichier ou lien
    document_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default="file",
        help_text="Type de document : fichier ou lien"
    )
    
    # Fichier (optionnel si c'est un lien)
    file = models.FileField(
        upload_to="documents/%Y/%m/",
        blank=True,
        null=True,
        help_text="Fichier du document (requis si type=fichier)"
    )
    
    # Lien (optionnel si c'est un fichier)
    link_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL du lien (requis si type=lien)"
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_documents",
        help_text="Utilisateur qui a uploadé le document"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Gestion des accès
    target_type = models.CharField(
        max_length=10,
        choices=TARGET_CHOICES,
        default="all",
        help_text="Type de ciblage"
    )
    target_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="accessible_documents",
        help_text="Utilisateurs spécifiques ayant accès"
    )
    target_roles = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Rôles ayant accès (séparés par des virgules)"
    )
    
    # Métadonnées
    is_active = models.BooleanField(default=True, help_text="Document actif")
    download_count = models.PositiveIntegerField(default=0, help_text="Nombre de téléchargements/clics")
    
    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"
    
    def clean(self):
        """Validation des champs"""
        from django.core.exceptions import ValidationError
        
        if self.document_type == "file" and not self.file:
            raise ValidationError("Un fichier est requis si le type est 'fichier'")
        elif self.document_type == "link" and not self.link_url:
            raise ValidationError("Une URL est requise si le type est 'lien'")
        elif self.document_type == "file" and self.link_url:
            raise ValidationError("Ne peut pas avoir à la fois un fichier ET un lien")
        elif self.document_type == "link" and self.file:
            raise ValidationError("Ne peut pas avoir à la fois un lien ET un fichier")
    
    def save(self, *args, **kwargs):
        """Override save pour validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        type_label = "📎" if self.document_type == "file" else "🔗"
        return f"{type_label} {self.title} ({self.category})"
    
    def can_user_access(self, user):
        """Vérifie si un utilisateur peut accéder à ce document"""
        if not self.is_active:
            return False
            
        # L'uploader peut toujours accéder
        if self.uploaded_by == user:
            return True
            
        # Si c'est pour tout le monde
        if self.target_type == "all":
            return True
            
        # Si c'est pour des utilisateurs spécifiques
        if self.target_type == "specific":
            return self.target_users.filter(id=user.id).exists()
            
        # Si c'est par rôle
        if self.target_type == "role" and hasattr(user, "profile"):
            if self.target_roles:
                roles = [role.strip() for role in self.target_roles.split(",")]
                return user.profile.role in roles
                
        return False
    
    def increment_download_count(self):
        """Incrémente le compteur de téléchargements"""
        self.download_count += 1
        self.save(update_fields=["download_count"])


class DocumentDownload(models.Model):
    """
    Modèle pour tracer les téléchargements de documents
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="downloads"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="document_downloads"
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ["-downloaded_at"]
        verbose_name = "Téléchargement de document"
        verbose_name_plural = "Téléchargements de documents"
    
    def __str__(self):
        return f"{self.user.username} - {self.document.title} - {self.downloaded_at}"


def get_leave_balance(user, period_start=None):
    """
    Récupère le solde de congés depuis la nouvelle table UserLeaveBalance.
    Si le solde n'existe pas, le crée avec les règles de calcul.
    
    Args:
        user: L'utilisateur
        period_start: Date de début de période spécifique (optionnel)
    """
    from datetime import date
    
    if period_start is None:
        today = date.today()
        
        # Déterminer les dates de période de référence
        if today.month >= 6:  # juin à décembre
            period_start = date(today.year, 6, 1)
            period_end = date(today.year + 1, 5, 31)
        else:  # janvier à mai
            period_start = date(today.year - 1, 6, 1)
            period_end = date(today.year, 5, 31)
    else:
        # Calculer period_end basé sur period_start
        period_end = date(period_start.year + 1, 5, 31)
    
    # Récupérer le solde existant
    try:
        balance = UserLeaveBalance.objects.get(
            user=user,
            period_start=period_start
        )
        # Mettre à jour les jours pris au cas où il y aurait eu des changements
        balance.update_taken_days()
        created = False
    except UserLeaveBalance.DoesNotExist:
        # Créer un nouveau solde avec calcul automatique initial
        balance, created = UserLeaveBalance.objects.get_or_create(
            user=user,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'days_acquired': _calculate_acquired_days_new(user, period_start, period_end),
                'days_taken': 0,
                'days_carry_over': _get_carry_over_new(user, period_start),
            }
        )
        
        # Si créé, recalculer les jours pris depuis le début de la période
        if created:
            balance.update_taken_days()
    
    return {
        'remaining': balance.days_remaining,
        'acquired': balance.days_acquired,
        'taken': balance.days_taken,
        'carry_over': balance.days_carry_over,
        'total': balance.total_available,
        'period_start': balance.period_start,
        'period_end': balance.period_end,
        'balance': balance.days_remaining,  # alias pour compatibilité
        'report': balance.days_carry_over,  # alias pour compatibilité
    }


def _calculate_acquired_days_new(user, period_start, period_end):
    """Calcule les jours acquis pour une période donnée avec les nouvelles dates"""
    if not hasattr(user, 'profile'):
        return 0
    
    site = user.profile.site
    today = date.today()
    
    # Date d'embauche effective
    date_joined = user.date_joined.date() if hasattr(user, 'date_joined') else period_start
    work_start = max(period_start, date_joined)
    work_end = min(period_end, today)
    
    if work_start > work_end:
        return 0
    
    # Calcul des mois travaillés
    months_worked = 0
    current_date = work_start.replace(day=1)  # Premier du mois de début
    
    while current_date <= work_end:
        # Si on a travaillé au moins 15 jours dans le mois, on compte le mois entier
        month_start = current_date
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        actual_work_start = max(work_start, month_start)
        actual_work_end = min(work_end, month_end)
        
        days_in_month = (actual_work_end - actual_work_start).days + 1
        
        if days_in_month >= 15:
            months_worked += 1
        elif days_in_month >= 1:  # Calcul proportionnel pour les mois partiels
            days_in_full_month = (month_end - month_start).days + 1
            months_worked += days_in_month / days_in_full_month
        
        # Passer au mois suivant
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Règles de calcul par site
    if site == 'tunisie':
        # Tunisie : 1.8 jours par mois travaillé (21.6 jours/an)
        acquired_days = months_worked * 1.8
    else:  # france
        # France : 2.5 jours par mois travaillé (30 jours/an)
        acquired_days = months_worked * 2.5
    
    from decimal import Decimal
    return Decimal(str(round(acquired_days, 1)))


def _get_carry_over_new(user, period_start):
    """Calcule le report de congés de la période précédente"""
    # Période précédente
    prev_period_start = date(period_start.year - 1, 6, 1)
    
    try:
        prev_balance = UserLeaveBalance.objects.get(
            user=user,
            period_start=prev_period_start
        )
        # Report limité à 5 jours maximum
        carry_over = min(5.0, max(0, float(prev_balance.days_remaining)))
        from decimal import Decimal
        return Decimal(str(carry_over))
    except UserLeaveBalance.DoesNotExist:
        # Pas de période précédente, pas de report
        from decimal import Decimal
        return Decimal('0')


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


# =====================
# Nouveaux modèles pour remplacer le système de cache
# =====================


class MonthlyUserStats(models.Model):
    """
    Table pour stocker les statistiques mensuelles de chaque utilisateur.
    Remplace le système de cache pour les rapports mensuels.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="monthly_stats",
        help_text="Utilisateur concerné"
    )
    
    year = models.IntegerField(help_text="Année")
    month = models.IntegerField(help_text="Mois (1-12)")
    
    # Statistiques de présence
    days_at_office = models.IntegerField(
        default=0,
        help_text="Nombre de jours travaillés au bureau"
    )
    days_telework = models.IntegerField(
        default=0,
        help_text="Nombre de jours en télétravail"
    )
    days_leave = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Nombre de jours de congés pris"
    )
    
    # Heures supplémentaires (télétravail weekend)
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text="Heures supplémentaires travaillées (weekend, télétravail)"
    )
    
    # Informations complémentaires
    total_workdays = models.IntegerField(
        default=0,
        help_text="Total des jours ouvrés dans le mois"
    )
    holidays_count = models.IntegerField(
        default=0,
        help_text="Nombre de jours fériés dans le mois"
    )
    
    # Métadonnées
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "year", "month")
        indexes = [
            models.Index(fields=["user", "year", "month"], name="idx_stats_user_period"),
            models.Index(fields=["year", "month"], name="idx_stats_period"),
            models.Index(fields=["last_updated"], name="idx_stats_updated"),
        ]
        verbose_name = "Statistiques mensuelles utilisateur"
        verbose_name_plural = "Statistiques mensuelles utilisateurs"
        ordering = ["-year", "-month", "user__last_name", "user__first_name"]
    
    @property
    def total_working_days(self):
        """Total des jours travaillés (bureau + télétravail)"""
        return self.days_at_office + self.days_telework
    
    @property
    def attendance_rate(self):
        """Taux de présence (%)"""
        if self.total_workdays == 0:
            return 0
        return round((self.total_working_days / self.total_workdays) * 100, 1)
    
    def __str__(self):
        return f"{self.user.username} - {self.year}/{self.month:02d} (Bureau: {self.days_at_office}j, TT: {self.days_telework}j)"
    
    def add_office_day(self):
        """Ajoute un jour de bureau"""
        self.days_at_office += 1
        self.save()
    
    def add_telework_day(self):
        """Ajoute un jour de télétravail"""
        self.days_telework += 1
        self.save()
    
    def add_leave_days(self, days):
        """Ajoute des jours de congés"""
        self.days_leave += days
        self.save()
    
    def add_overtime_hours(self, hours):
        """Ajoute des heures supplémentaires"""
        self.overtime_hours += hours
        self.save()
    
    def update_from_requests(self):
        """Met à jour les statistiques basées sur les demandes approuvées du mois"""
        from datetime import date
        from decimal import Decimal
        from workalendar.europe import France
        
        # Dates du mois
        start_date = date(self.year, self.month, 1)
        if self.month == 12:
            end_date = date(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(self.year, self.month + 1, 1) - timedelta(days=1)
        
        # Jours fériés du mois
        france_calendar = France()
        holidays = set()
        current_date = start_date
        while current_date <= end_date:
            if france_calendar.is_holiday(current_date):
                holidays.add(current_date)
            current_date += timedelta(days=1)
        
        # Congés approuvés du mois
        LeaveRequestModel = self.__class__._meta.apps.get_model('extranet', 'LeaveRequest')
        leaves = LeaveRequestModel.objects.filter(
            user=self.user,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        total_leave_days = Decimal('0')
        demi_jour_days = set()
        leave_days = set()
        
        for leave in leaves:
            # Intersection avec le mois
            leave_start = max(leave.start_date, start_date)
            leave_end = min(leave.end_date, end_date)
            
            if leave.demi_jour in ['am', 'pm']:
                if leave_start == leave_end:  # Demi-journée dans le mois
                    total_leave_days += Decimal('0.5')
                    demi_jour_days.add(leave_start)
            else:
                # Jours complets
                current_date = leave_start
                while current_date <= leave_end:
                    if current_date.weekday() < 5:  # jours ouvrés
                        total_leave_days += Decimal('1')
                        leave_days.add(current_date)
                    current_date += timedelta(days=1)
        
        # Télétravail approuvé du mois
        TeleworkRequestModel = self.__class__._meta.apps.get_model('extranet', 'TeleworkRequest')
        teleworks = TeleworkRequestModel.objects.filter(
            user=self.user,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        total_telework_days = 0
        telework_days = set()
        
        for telework in teleworks:
            # Intersection avec le mois
            telework_start = max(telework.start_date, start_date)
            telework_end = min(telework.end_date, end_date)
            
            # Compter les jours ouvrés
            current_date = telework_start
            while current_date <= telework_end:
                if current_date.weekday() < 5:  # lundi à vendredi
                    total_telework_days += 1
                    telework_days.add(current_date)
                current_date += timedelta(days=1)
        
        # Heures supplémentaires approuvées du mois
        OverTimeRequestModel = self.__class__._meta.apps.get_model('extranet', 'OverTimeRequest')
        overtimes = OverTimeRequestModel.objects.filter(
            user=self.user,
            status='approved',
            work_date__gte=start_date,
            work_date__lte=end_date
        )
        
        total_overtime_hours = sum(overtime.hours for overtime in overtimes)
        
        # Calculer les jours au bureau (jours ouvrés - congés - télétravail - fériés)
        total_workdays_month = 0
        office_days = 0
        today = date.today()
        
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # lundi à vendredi
                total_workdays_month += 1
                
                # Seuls les jours passés ou actuels comptent pour les jours au bureau
                if current_date <= today:
                    # Exclure les jours fériés, congés (complets et demi-journées) et télétravail
                    if (current_date not in holidays and 
                        current_date not in leave_days and 
                        current_date not in demi_jour_days and 
                        current_date not in telework_days):
                        office_days += 1
                        
            current_date += timedelta(days=1)
        
        # Mettre à jour les champs
        self.days_leave = total_leave_days
        self.days_telework = total_telework_days
        self.days_at_office = office_days
        self.total_workdays = total_workdays_month
        self.holidays_count = len([d for d in holidays if d.month == self.month])
        self.overtime_hours = total_overtime_hours
        self.save()
    
    def remove_leave_days(self, days):
        """Retire des jours de congés"""
        self.days_leave = max(0, self.days_leave - days)
        self.save()


# =====================
# Nouveaux modèles pour la gestion des congés et statistiques
# =====================

class UserLeaveBalance(models.Model):
    """
    Modèle pour gérer les soldes de congés par utilisateur.
    Remplace le système de cache et gère les acquis/pris/à prendre.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leave_balances",
        help_text="Utilisateur associé à ce solde"
    )
    
    # Période de référence
    period_start = models.DateField(
        help_text="Date de début de la période de référence (01/06)"
    )
    period_end = models.DateField(
        help_text="Date de fin de la période de référence (31/05)"
    )
    
    # Congés
    days_acquired = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text="Jours de congés acquis dans la période"
    )
    days_taken = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text="Jours de congés pris dans la période"
    )
    days_carry_over = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text="Report de la période précédente"
    )
    
    # Métadonnées
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Solde de congés utilisateur"
        verbose_name_plural = "Soldes de congés utilisateurs"
        ordering = ['-period_start', 'user__last_name', 'user__first_name']
        unique_together = ['user', 'period_start']
    
    @property
    def days_remaining(self):
        """Calcule les jours de congés restants"""
        from decimal import Decimal
        
        # S'assurer que toutes les valeurs sont des Decimal ou 0
        acquired = self.days_acquired or Decimal('0')
        carry_over = self.days_carry_over or Decimal('0')
        taken = self.days_taken or Decimal('0')
        
        return acquired + carry_over - taken
    
    @property
    def total_available(self):
        """Total des jours disponibles (acquis + report)"""
        from decimal import Decimal
        
        # S'assurer que toutes les valeurs sont des Decimal ou 0
        acquired = self.days_acquired or Decimal('0')
        carry_over = self.days_carry_over or Decimal('0')
        
        return acquired + carry_over
    
    def update_taken_days(self):
        """Met à jour le nombre de jours pris basé sur les demandes approuvées"""
        from decimal import Decimal
        
        approved_leaves = self.user.leave_requests.filter(
            status='approved',
            start_date__gte=self.period_start,
            start_date__lte=self.period_end
        )
        
        total_taken = Decimal('0')
        for leave in approved_leaves:
            if leave.demi_jour in ['am', 'pm']:
                total_taken += Decimal('0.5')
            else:
                # Calcul selon le site
                if hasattr(self.user, 'profile') and self.user.profile.site == 'france':
                    # France : jours ouvrables avec règle spéciale vendredi-samedi
                    total_days = 0
                    current_date = leave.start_date
                    
                    while current_date <= leave.end_date:
                        weekday = current_date.weekday()
                        
                        if weekday < 5:  # lundi à vendredi
                            total_days += 1
                            
                            # Règle spéciale : si c'est un vendredi, le samedi suivant est automatiquement congé
                            if weekday == 4:  # vendredi
                                saturday = current_date + timedelta(days=1)
                                # Vérifier si le samedi est dans la période OU le vendredi est le dernier jour de la demande
                                if saturday <= leave.end_date or current_date == leave.end_date:
                                    total_days += 1  # ajouter le samedi automatiquement
                                    
                        elif weekday == 5:  # samedi
                            # Samedi uniquement s'il n'a pas déjà été compté avec un vendredi précédent
                            previous_day = current_date - timedelta(days=1)
                            if previous_day < leave.start_date or previous_day.weekday() != 4:
                                total_days += 1
                                
                        current_date += timedelta(days=1)
                        
                    total_taken += Decimal(str(total_days))
                else:
                    # Tunisie : jours ouvrés (lundi-vendredi)
                    total_days = 0
                    current_date = leave.start_date
                    while current_date <= leave.end_date:
                        if current_date.weekday() < 5:
                            total_days += 1
                        current_date += timedelta(days=1)
                    total_taken += Decimal(str(total_days))
        
        self.days_taken = total_taken
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.period_start.year}/{self.period_start.year+1} (Restant: {self.days_remaining}j)"


register = template.Library()


@register.filter
def get_nb_days(leave):
    """
    Retourne 0.5 si demi-journée (am/pm), sinon le nombre de jours calendaires
    entre start_date et end_date inclus.
    """
    if leave.demi_jour in ["am", "pm"]:
        return 0.5
    return (leave.end_date - leave.start_date).days + 1
