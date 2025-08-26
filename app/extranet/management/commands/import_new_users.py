"""
Commande Django pour importer de nouveaux utilisateurs de manière sécurisée
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from extranet.models import UserLeaveBalance, MonthlyUserStats
import csv
from decimal import Decimal
from datetime import date


User = get_user_model()


class Command(BaseCommand):
    help = 'Importe de nouveaux utilisateurs depuis un CSV sans écraser les données existantes'

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
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Valider le format CSV uniquement'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        dry_run = options['dry_run']
        validate_only = options['validate_only']
        
        if not os.path.exists(csv_file):
            raise CommandError(f'Fichier CSV introuvable: {csv_file}')
        
        self.stdout.write(self.style.SUCCESS(f'📂 Fichier: {csv_file}'))
        
        if validate_only:
            self.validate_csv_format(csv_file)
            return
        
        self.stdout.write(
            f'🔍 Mode: {self.style.WARNING("SIMULATION") if dry_run else self.style.ERROR("IMPORT RÉEL")}'
        )
        self.stdout.write('-' * 60)
        
        success = self.import_users_from_csv(csv_file, dry_run)
        
        if success:
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS('✅ Simulation terminée avec succès')
                )
                self.stdout.write(
                    'Pour l\'import réel, retirez l\'option --dry-run'
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('🎉 Import terminé avec succès!')
                )
        else:
            raise CommandError('❌ Échec de l\'import')

    def validate_csv_format(self, csv_file):
        """Valide le format du CSV"""
        self.stdout.write('🔍 Validation du format CSV...')
        
        # Vérification des colonnes requises
            required_columns = [
                'username', 'nom', 'prenom', 'days_acquired', 'days_taken', 
                'days_carry_over', 'site', 'mail', 'password', 'role', 'manager', 'rh'
            ]
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Colonnes manquantes: {missing_columns}')
                    )
                    self.stdout.write(f'📋 Colonnes disponibles: {reader.fieldnames}')
                    return False
                
                self.stdout.write(self.style.SUCCESS('✅ Format CSV valide!'))
                self.stdout.write(f'📋 Colonnes: {reader.fieldnames}')
                return True
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur de validation: {e}'))
            return False

    def import_users_from_csv(self, csv_file, dry_run=True):
        """Importe les utilisateurs depuis le CSV"""
        new_users = []
        existing_users = []
        invalid_rows = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
        required_columns = [
            'username', 'nom', 'prenom', 'days_acquired', 'days_taken', 
            'days_carry_over', 'site', 'mail', 'password', 'role', 'manager', 'rh'
        ]                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Colonnes manquantes: {missing_columns}')
                    )
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        username = row['username'].strip()
                        email = row['email'].strip()
                        
                        if not username or not email:
                            invalid_rows.append(f'Ligne {row_num}: username ou email vide')
                            continue
                        
                        # Vérifier si l'utilisateur existe déjà
                        if User.objects.filter(username=username).exists():
                            existing_users.append(username)
                            continue
                        
                        if User.objects.filter(email=email).exists():
                            existing_users.append(f'{username} (email {email} déjà utilisé)')
                            continue
                        
                        # Données utilisateur
                        user_data = {
                            'username': username,
                            'email': email,
                            'first_name': row['first_name'].strip(),
                            'last_name': row['last_name'].strip(),
                            'annual_leave_days': Decimal(row['annual_leave_days']),
                            'used_leave_days': Decimal(row['used_leave_days']),
                            'year': int(row['year']),
                            'month': int(row['month'])
                        }
                        
                        # Validation des données
                        if user_data['annual_leave_days'] < 0 or user_data['used_leave_days'] < 0:
                            invalid_rows.append(f'Ligne {row_num}: Valeurs négatives non autorisées')
                            continue
                        
                        if user_data['used_leave_days'] > user_data['annual_leave_days']:
                            invalid_rows.append(f'Ligne {row_num}: Jours utilisés > jours annuels')
                            continue
                        
                        new_users.append(user_data)
                        
                    except ValueError as e:
                        invalid_rows.append(f'Ligne {row_num}: Erreur de format - {e}')
                    except Exception as e:
                        invalid_rows.append(f'Ligne {row_num}: Erreur - {e}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lecture CSV: {e}'))
            return False
        
        # Rapport de pré-import
        self.stdout.write('📊 RAPPORT DE PRÉ-IMPORT:')
        self.stdout.write(f'   ✅ Nouveaux utilisateurs: {len(new_users)}')
        self.stdout.write(f'   ⚠️  Utilisateurs existants: {len(existing_users)}')
        self.stdout.write(f'   ❌ Lignes invalides: {len(invalid_rows)}')
        
        if existing_users:
            self.stdout.write(self.style.WARNING('\n👥 UTILISATEURS EXISTANTS (ignorés):'))
            for username in existing_users[:10]:
                self.stdout.write(f'   - {username}')
            if len(existing_users) > 10:
                self.stdout.write(f'   ... et {len(existing_users) - 10} autres')
        
        if invalid_rows:
            self.stdout.write(self.style.ERROR('\n⚠️  LIGNES INVALIDES:'))
            for error in invalid_rows[:5]:
                self.stdout.write(f'   - {error}')
            if len(invalid_rows) > 5:
                self.stdout.write(f'   ... et {len(invalid_rows) - 5} autres erreurs')
        
        if new_users:
            self.stdout.write(self.style.SUCCESS('\n🆕 NOUVEAUX UTILISATEURS:'))
            for user_data in new_users[:5]:
                self.stdout.write(
                    f'   - {user_data["username"]} '
                    f'({user_data["first_name"]} {user_data["last_name"]})'
                )
            if len(new_users) > 5:
                self.stdout.write(f'   ... et {len(new_users) - 5} autres')
        
        if not new_users:
            self.stdout.write(self.style.WARNING('ℹ️  Aucun nouvel utilisateur à importer.'))
            return True
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('\n🔍 SIMULATION TERMINÉE')
            )
            return True
        
        # Import réel
        self.stdout.write('\n🚀 DÉBUT DE L\'IMPORT RÉEL...')
        created_users = 0
        created_balances = 0
        created_stats = 0
        
        try:
            with transaction.atomic():
                for user_data in new_users:
                    try:
                        # Créer l'utilisateur
                        user = User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name'],
                            password='ChangeMe123!'  # Mot de passe temporaire
                        )
                        created_users += 1
                        self.stdout.write(f'   ✅ Utilisateur: {user.username}')
                        
                        # Créer le solde de congés
                        remaining_days = user_data['annual_leave_days'] - user_data['used_leave_days']
                        leave_balance = UserLeaveBalance.objects.create(
                            user=user,
                            year=user_data['year'],
                            annual_leave_days=user_data['annual_leave_days'],
                            used_leave_days=user_data['used_leave_days'],
                            remaining_leave_days=remaining_days
                        )
                        created_balances += 1
                        self.stdout.write(f'      📊 Solde: {remaining_days} jours restants')
                        
                        # Créer les statistiques mensuelles
                        monthly_stats = MonthlyUserStats.objects.create(
                            user=user,
                            year=user_data['year'],
                            month=user_data['month'],
                            total_leave_days=user_data['used_leave_days'],
                            overtime_hours=Decimal('0.00'),
                            telework_days=0
                        )
                        created_stats += 1
                        self.stdout.write(
                            f'      📈 Stats: {user_data["month"]}/{user_data["year"]}'
                        )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'   ❌ Erreur {user_data["username"]}: {e}')
                        )
                        raise  # Annule la transaction
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur import: {e}'))
            return False
        
        self.stdout.write(self.style.SUCCESS('\n🎉 IMPORT TERMINÉ!'))
        self.stdout.write(f'   👥 Utilisateurs créés: {created_users}')
        self.stdout.write(f'   📊 Soldes créés: {created_balances}')
        self.stdout.write(f'   📈 Statistiques créées: {created_stats}')
        
        # Suggestions post-import
        self.stdout.write(self.style.WARNING('\n📝 ACTIONS RECOMMANDÉES:'))
        self.stdout.write('   1. Demander aux nouveaux utilisateurs de changer leur mot de passe')
        self.stdout.write('   2. Vérifier les soldes de congés')
        self.stdout.write('   3. Configurer les permissions si nécessaire')
        
        return True
