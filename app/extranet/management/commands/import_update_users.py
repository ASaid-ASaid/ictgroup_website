"""
Commande Django pour importer/mettre à jour des utilisateurs depuis un CSV
Avec écrasement des données existantes si nécessaire
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from extranet.models import UserLeaveBalance, MonthlyUserStats, UserProfile
import csv
from decimal import Decimal
from datetime import date


User = get_user_model()

# Mapping des rôles pour Django User (permissions)
USER_ROLE_MAPPING = {
    'admin': 'ADMIN',
    'manager': 'MANAGER', 
    'user': 'EMPLOYEE',
    'employee': 'EMPLOYEE',
    'rh': 'RH',
    'chef_projet': 'MANAGER',
    'developpeur': 'EMPLOYEE',
    'designer': 'EMPLOYEE',
    'qa': 'EMPLOYEE',
    'consultant': 'EMPLOYEE',
    'analyste': 'EMPLOYEE',
    'devops': 'EMPLOYEE',
    'stagiaire': 'EMPLOYEE'
}

# Mapping des rôles pour UserProfile (stockage)
PROFILE_ROLE_MAPPING = {
    'admin': 'admin',
    'manager': 'manager', 
    'user': 'user',
    'employee': 'user',
    'rh': 'rh',
    'chef_projet': 'manager',
    'developpeur': 'user',
    'designer': 'user',
    'qa': 'user',
    'consultant': 'user',
    'analyste': 'user',
    'devops': 'user',
    'stagiaire': 'user'
}

# Mapping des sites
SITE_MAPPING = {
    'france': 'france',
    'tunisie': 'tunisie',
    'fr': 'FR',
    'tn': 'TN'
}


class Command(BaseCommand):
    help = 'Importe/Met à jour des utilisateurs depuis un CSV avec écrasement possible'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Chemin vers le fichier CSV'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans modifications réelles'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        dry_run = options['dry_run']
        
        if not os.path.exists(csv_file):
            raise CommandError(f'Fichier CSV introuvable: {csv_file}')
        
        self.stdout.write(self.style.SUCCESS(f'📂 Fichier: {csv_file}'))
        
        mode_text = "SIMULATION" if dry_run else "IMPORT"
        self.stdout.write(f'🔍 Mode: {self.style.WARNING(mode_text)}')
        self.stdout.write('-' * 60)
        
        success = self.import_users_from_csv(csv_file, dry_run)
        
        if success:
            if dry_run:
                self.stdout.write(self.style.SUCCESS('✅ Simulation terminée avec succès'))
            else:
                self.stdout.write(self.style.SUCCESS('🎉 Import/Mise à jour terminé(e) avec succès!'))
        else:
            raise CommandError('❌ Échec de l\'opération')

    def import_users_from_csv(self, csv_file, dry_run=True):
        """Importe/Met à jour les utilisateurs depuis le CSV"""
        new_users = []
        existing_users = []
        invalid_rows = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):
                    # Validation de la ligne
                    errors = self.validate_row_data(row, row_num)
                    if errors:
                        invalid_rows.append(f'Ligne {row_num}: {"; ".join(errors)}')
                        continue
                    
                    username = row['username'].strip()
                    email = row['mail'].strip()
                    
                    # Vérifier si l'utilisateur existe
                    existing_user = User.objects.filter(username=username).first()
                    
                    # Traitement des données
                    user_data = self.process_row_data(row)
                    
                    if existing_user:
                        user_data['action'] = 'update'
                        user_data['existing_user'] = existing_user
                        existing_users.append(user_data)
                    else:
                        user_data['action'] = 'create'
                        new_users.append(user_data)
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lecture CSV: {e}'))
            return False
        
        # Rapport de pré-import
        self.stdout.write('📊 RAPPORT DE PRÉ-TRAITEMENT:')
        self.stdout.write(f'   🆕 Nouveaux utilisateurs: {len(new_users)}')
        self.stdout.write(f'   🔄 Utilisateurs à mettre à jour: {len(existing_users)}')
        self.stdout.write(f'   ❌ Lignes invalides: {len(invalid_rows)}')
        
        if invalid_rows:
            self.stdout.write(self.style.ERROR('\n⚠️  LIGNES INVALIDES:'))
            for error in invalid_rows[:5]:
                self.stdout.write(f'   - {error}')
            if len(invalid_rows) > 5:
                self.stdout.write(f'   ... et {len(invalid_rows) - 5} autres erreurs')
        
        if new_users:
            self.stdout.write(self.style.SUCCESS('\n🆕 NOUVEAUX UTILISATEURS:'))
            for user_data in new_users[:5]:
                self.stdout.write(f'   - {user_data["username"]} ({user_data["prenom"]} {user_data["nom"]})')
            if len(new_users) > 5:
                self.stdout.write(f'   ... et {len(new_users) - 5} autres')
        
        if existing_users:
            self.stdout.write(self.style.WARNING('\n🔄 UTILISATEURS À METTRE À JOUR:'))
            for user_data in existing_users[:5]:
                self.stdout.write(f'   - {user_data["username"]} ({user_data["prenom"]} {user_data["nom"]})')
            if len(existing_users) > 5:
                self.stdout.write(f'   ... et {len(existing_users) - 5} autres')
        
        if not new_users and not existing_users:
            self.stdout.write(self.style.WARNING('ℹ️  Aucune donnée à traiter.'))
            return True
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n🔍 SIMULATION TERMINÉE'))
            return True
        
        # Traitement réel
        return self.process_users(new_users + existing_users)

    def process_row_data(self, row):
        """Traite les données d'une ligne CSV"""
        # Récupérer les utilisateurs manager et rh
        manager_user = None
        rh_user = None
        
        manager_username = row['manager'].strip()
        rh_username = row['rh'].strip()
        
        if manager_username:
            try:
                manager_user = User.objects.get(username=manager_username)
            except User.DoesNotExist:
                pass  # On ignore si l'utilisateur n'existe pas
        
        if rh_username:
            try:
                rh_user = User.objects.get(username=rh_username)
            except User.DoesNotExist:
                pass  # On ignore si l'utilisateur n'existe pas
        
        return {
            'username': row['username'].strip(),
            'nom': row['nom'].strip(),
            'prenom': row['prenom'].strip(),
            'email': row['mail'].strip(),
            'password': row['password'].strip() or 'ChangeMe123!',
            'days_acquired': Decimal(str(row['days_acquired'])) if row['days_acquired'].strip() else Decimal('0'),
            'days_taken': Decimal(str(row['days_taken'])) if row['days_taken'].strip() else Decimal('0'),
            'site': SITE_MAPPING[row['site'].strip().lower()],
            'role': USER_ROLE_MAPPING[row['role'].strip().lower()],
            'profile_role': PROFILE_ROLE_MAPPING[row['role'].strip().lower()],
            'manager_user': manager_user,
            'rh_user': rh_user
        }

    def process_users(self, users_data):
        """Traite la création/mise à jour des utilisateurs"""
        self.stdout.write('\n🚀 DÉBUT DU TRAITEMENT...')
        
        created_count = 0
        updated_count = 0
        balance_count = 0
        stats_count = 0
        
        try:
            with transaction.atomic():
                for user_data in users_data:
                    try:
                        if user_data['action'] == 'create':
                            user = self.create_user(user_data)
                            created_count += 1
                            self.stdout.write(f'   ✅ Créé: {user.username}')
                        else:
                            user = self.update_user(user_data)
                            updated_count += 1
                            self.stdout.write(f'   🔄 Mis à jour: {user.username}')
                        
                        # Gestion des soldes de congés
                        if self.update_leave_balance(user, user_data):
                            balance_count += 1
                        
                        # Gestion des statistiques mensuelles
                        if self.update_monthly_stats(user, user_data):
                            stats_count += 1
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   ❌ Erreur {user_data["username"]}: {e}'))
                        raise
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur traitement: {e}'))
            return False
        
        self.stdout.write(self.style.SUCCESS('\n🎉 TRAITEMENT TERMINÉ!'))
        self.stdout.write(f'   👥 Utilisateurs créés: {created_count}')
        self.stdout.write(f'   🔄 Utilisateurs mis à jour: {updated_count}')
        self.stdout.write(f'   📊 Soldes traités: {balance_count}')
        self.stdout.write(f'   📈 Statistiques mises à jour: {stats_count}')
        
        return True

    def create_user(self, user_data):
        """Crée un nouvel utilisateur"""
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['prenom'],
            last_name=user_data['nom'],
            password=user_data['password']
        )
        
        # Définition des permissions selon le rôle
        if user_data['role'] == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        elif user_data['role'] in ['MANAGER', 'RH']:
            user.is_staff = True
        
        user.save()
        
        # Création du profil utilisateur
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': user_data['profile_role'],
                'site': user_data['site'],
                'manager': user_data['manager_user'],
                'rh': user_data['rh_user']
            }
        )
        
        return user

    def update_user(self, user_data):
        """Met à jour un utilisateur existant"""
        user = user_data['existing_user']
        
        # Mise à jour des informations de base
        user.email = user_data['email']
        user.first_name = user_data['prenom']
        user.last_name = user_data['nom']
        
        # Mise à jour du mot de passe si fourni
        if user_data['password'] != 'ChangeMe123!':
            user.set_password(user_data['password'])
        
        # Mise à jour des permissions
        if user_data['role'] == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        elif user_data['role'] in ['MANAGER', 'RH']:
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False
        
        user.save()
        
        # Mise à jour du profil utilisateur
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = user_data['profile_role']
        profile.site = user_data['site']
        profile.manager = user_data['manager_user']
        profile.rh = user_data['rh_user']
        profile.save()
        
        return user

    def update_leave_balance(self, user, user_data):
        """Met à jour ou crée le solde de congés"""
        from datetime import date
        
        current_date = date.today()
        
        # Déterminer la période de référence
        if current_date.month >= 6:  # juin à décembre
            period_start = date(current_date.year, 6, 1)
            period_end = date(current_date.year + 1, 5, 31)
        else:  # janvier à mai
            period_start = date(current_date.year - 1, 6, 1)
            period_end = date(current_date.year, 5, 31)
        
        balance, created = UserLeaveBalance.objects.update_or_create(
            user=user,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'days_acquired': user_data['days_acquired'],
                'days_taken': user_data['days_taken'],
                'days_carry_over': Decimal('0')  # Initialiser à 0, sera géré via UserLeaveBalance
            }
        )
        
        return True

    def update_monthly_stats(self, user, user_data):
        """Met à jour les statistiques mensuelles"""
        current_date = date.today()
        
        stats, created = MonthlyUserStats.objects.update_or_create(
            user=user,
            year=current_date.year,
            month=current_date.month,
            defaults={
                'days_leave': user_data['days_taken'],
                'overtime_hours': Decimal('0.00'),
                'days_telework': 0,
                'days_at_office': 0,
                'total_workdays': 22  # Valeur par défaut
            }
        )
        
        return True
