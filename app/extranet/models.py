# =====================
# Modèles principaux de l'app 'extranet'
# Chaque classe correspond à une table de la base de données.
# Les modèles gèrent la logique métier et les relations entre les entités.
# =====================
from django.db import models
from django.contrib.auth.models import User
from datetime import date

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')  # L'utilisateur qui fait la demande
    start_date = models.DateField()  # Date de début du congé
    end_date = models.DateField()    # Date de fin du congé
    reason = models.TextField(blank=True, null=True)  # Raison optionnelle
    submitted_at = models.DateTimeField(auto_now_add=True)  # Date de soumission

    # Statuts possibles pour la demande
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
        ('cancelled', 'Annulée'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Statut de la demande (workflow de validation)"
    )
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification

    # Champs de validation multi-acteurs
    manager_validated = models.BooleanField(default=False, help_text="Validation du manager")
    rh_validated = models.BooleanField(default=False, help_text="Validation RH")
    admin_validated = models.BooleanField(default=False, help_text="Validation admin")

    DEMI_JOUR_CHOICES = [
        ('full', 'Journée complète'),
        ('am', 'Matin'),
        ('pm', 'Après-midi'),
    ]
    demi_jour = models.CharField(
        max_length=4,
        choices=DEMI_JOUR_CHOICES,
        default='full',
        help_text="Demi-journée ou journée complète"
    )

    def __str__(self):
        # Représentation lisible de la demande
        return f"Demande de congé de {self.user.username} du {self.start_date} au {self.end_date} ({self.status})"

    class Meta:
        ordering = ['-submitted_at']  # Trie par date de soumission décroissante

    @property
    def get_nb_days(self):
        """
        Retourne 0.5 si demi-journée (am/pm), sinon le nombre de jours calendaires entre start_date et end_date inclus.
        """
        if self.demi_jour in ['am', 'pm']:
            return 0.5
        return (self.end_date - self.start_date).days + 1

class TeleworkRequest(models.Model):
    """
    Modèle pour la demande de télétravail.
    - Gère les plages de dates.
    - Statuts et validation manager.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telework_requests')
    start_date = models.DateField()  # Date de début du télétravail
    end_date = models.DateField()    # Date de fin du télétravail
    reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
        ('cancelled', 'Annulée'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', help_text="Statut de la demande")
    updated_at = models.DateTimeField(auto_now=True)
    manager_validated = models.BooleanField(default=False, help_text="Validation du manager")

    def __str__(self):
        if self.start_date == self.end_date:
            return f"Télétravail {self.user.username} le {self.start_date} ({self.status})"
        return f"Télétravail {self.user.username} du {self.start_date} au {self.end_date} ({self.status})"

    class Meta:
        ordering = ['-start_date']

# Profil utilisateur pour gérer les rôles et rattachements
class UserProfile(models.Model):
    SITE_CHOICES = [
        ('tunisie', 'Tunisie'),
        ('france', 'France'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=[('user','Utilisateur'),('manager','Manager'),('rh','RH'),('admin','Admin')], default='user')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_users')
    rh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rh_users')
    site = models.CharField(max_length=10, choices=SITE_CHOICES, default='tunisie')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

def get_leave_balance(user):
    """
    Calcule le solde de congés pour un utilisateur :
    - Jours acquis (1.8/mois)
    - Jours pris (congés validés sur l'année)
    - Solde restant
    - Report à prendre avant le 30 avril (reliquat année précédente)
    """
    today = date.today()
    year = today.year
    # Date d'embauche (si disponible)
    date_joined = user.date_joined.date() if hasattr(user, 'date_joined') else date(year, 1, 1)
    # Début de l'année
    year_start = date(year, 1, 1)
    # Mois travaillés cette année
    months_worked = max(0, (today.year - date_joined.year) * 12 + today.month - (date_joined.month if date_joined.year == year else 1) + 1)
    # Récupère le site (Tunisie/France)
    site = getattr(user.profile, 'site', 'tunisie') if hasattr(user, 'profile') else 'tunisie'
    # Jours acquis selon le site
    days_per_month = 2.5 if site == 'france' else 1.8
    days_acquired = round(months_worked * days_per_month, 1)
    # Jours pris cette année (congés validés)
    leaves = user.leave_requests.filter(status='approved', start_date__year=year)
    def leave_days(leave):
        if leave.demi_jour != 'full' and leave.start_date == leave.end_date:
            return 0.5
        # Règle France : si vendredi seul, samedi compte aussi
        if site == 'france' and leave.start_date == leave.end_date and leave.start_date.weekday() == 4:
            return 2
        return (leave.end_date - leave.start_date).days + 1
    days_taken = sum([leave_days(leave) for leave in leaves])
    # Report de l'année précédente (congés non pris)
    prev_year = year - 1
    prev_leaves = user.leave_requests.filter(status='approved', start_date__year=prev_year)
    prev_days_taken = sum([leave_days(leave) for leave in prev_leaves])
    prev_days_acquired = 12 * days_per_month if date_joined.year < prev_year else max(0, (12 - date_joined.month + 1) * days_per_month)
    report = max(0, round(prev_days_acquired - prev_days_taken, 1))
    # Jours à prendre avant le 30 avril
    must_take_before_april = report if today <= date(year, 4, 30) else 0
    # Solde restant
    balance = round(days_acquired + report - days_taken, 1)
    return {
        'acquired': days_acquired,
        'taken': days_taken,
        'balance': balance,
        'report': report,
        'must_take_before_april': must_take_before_april,
        'site': site
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
    movement_type = models.CharField(max_length=10, choices=[('entry', 'Entrée'), ('exit', 'Sortie')])
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.movement_type} - {self.stock_item.code} by {self.user.username}"