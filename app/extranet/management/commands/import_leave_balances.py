"""
Commande Django pour importer/mettre à jour les soldes de congés depuis un CSV
Format: username,days_acquired,days_taken,days_carry_over,site,notes
"""
import os
import csv
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from extranet.models import UserLeaveBalance


class Command(BaseCommand):
    help = 'Importe/Met à jour les soldes de congés depuis un CSV'

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
        
        mode_text = "SIMULATION" if dry_run else "IMPORT RÉEL"
        self.stdout.write(f'🔍 Mode: {self.style.WARNING(mode_text)}')
        self.stdout.write('-' * 60)
        
        success = self.import_leave_balances_from_csv(csv_file, dry_run)
        
        if success:
            if dry_run:
                self.stdout.write(self.style.SUCCESS('✅ Simulation terminée avec succès'))
            else:
                self.stdout.write(self.style.SUCCESS('🎉 Import/Mise à jour terminé(e) avec succès!'))
        else:
            raise CommandError('❌ Échec de l\'opération')

    def import_leave_balances_from_csv(self, csv_file, dry_run=True):
        """Importe/Met à jour les soldes de congés depuis le CSV"""
        today = date.today()
        
        # Déterminer la période de congés actuelle
        if today.month >= 6:  # juin à décembre
            period_start = date(today.year, 6, 1)
        else:  # janvier à mai
            period_start = date(today.year - 1, 6, 1)
        
        period_end = date(period_start.year + 1, 5, 31)
        
        valid_rows = []
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
                    
                    # Vérifier si l'utilisateur existe
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        invalid_rows.append(f'Ligne {row_num}: Utilisateur "{username}" introuvable')
                        continue
                    
                    # Traitement des données
                    balance_data = {
                        'user': user,
                        'username': username,
                        'days_acquired': Decimal(str(row['days_acquired'])),
                        'days_taken': Decimal(str(row['days_taken'])),
                        'days_carry_over': Decimal(str(row['days_carry_over'])),
                        'site': row['site'].strip(),
                        'notes': row.get('notes', '').strip(),
                        'period_start': period_start,
                        'period_end': period_end
                    }
                    
                    valid_rows.append(balance_data)
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lecture CSV: {e}'))
            return False
        
        # Rapport de pré-import
        self.stdout.write('📊 RAPPORT DE PRÉ-TRAITEMENT:')
        self.stdout.write(f'   ✅ Lignes valides: {len(valid_rows)}')
        self.stdout.write(f'   ❌ Lignes invalides: {len(invalid_rows)}')
        self.stdout.write(f'   📅 Période: {period_start} → {period_end}')
        
        if invalid_rows:
            self.stdout.write(self.style.ERROR('\n⚠️  LIGNES INVALIDES:'))
            for error in invalid_rows[:5]:
                self.stdout.write(f'   - {error}')
            if len(invalid_rows) > 5:
                self.stdout.write(f'   ... et {len(invalid_rows) - 5} autres erreurs')
        
        if valid_rows:
            self.stdout.write(self.style.SUCCESS('\n📋 DONNÉES À TRAITER:'))
            for data in valid_rows[:5]:
                self.stdout.write(f'   - {data["username"]}: +{data["days_acquired"]}j, -{data["days_taken"]}j, report: {data["days_carry_over"]}j')
            if len(valid_rows) > 5:
                self.stdout.write(f'   ... et {len(valid_rows) - 5} autres utilisateurs')
        
        if not valid_rows:
            self.stdout.write(self.style.WARNING('ℹ️  Aucune donnée valide à traiter.'))
            return True
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n🔍 SIMULATION TERMINÉE'))
            return True
        
        # Traitement réel
        return self.process_leave_balances(valid_rows)

    def validate_row_data(self, row, row_num):
        """Valide les données d'une ligne CSV"""
        errors = []
        
        # Vérifier les champs obligatoires
        required_fields = ['username', 'days_acquired', 'days_taken', 'days_carry_over', 'site']
        for field in required_fields:
            if not row.get(field, '').strip():
                errors.append(f"Champ '{field}' manquant ou vide")
        
        # Valider les champs numériques
        numeric_fields = ['days_acquired', 'days_taken', 'days_carry_over']
        for field in numeric_fields:
            value = row.get(field, '').strip()
            if value:
                try:
                    float(value)
                except ValueError:
                    errors.append(f"Champ '{field}' doit être numérique, reçu: '{value}'")
        
        # Valider le site
        site = row.get('site', '').strip().lower()
        if site and site not in ['france', 'tunisie', 'fr', 'tn']:
            errors.append(f"Site '{site}' invalide. Valeurs autorisées: france, tunisie, fr, tn")
        
        return errors

    def process_leave_balances(self, balances_data):
        """Traite la création/mise à jour des soldes de congés"""
        self.stdout.write('\n🚀 DÉBUT DU TRAITEMENT...')
        
        created_count = 0
        updated_count = 0
        
        try:
            with transaction.atomic():
                for data in balances_data:
                    try:
                        # Récupérer ou créer le solde pour la période courante
                        balance, created = UserLeaveBalance.objects.get_or_create(
                            user=data['user'],
                            period_start=data['period_start'],
                            defaults={
                                'period_end': data['period_end'],
                                'days_acquired': Decimal('0'),
                                'days_taken': Decimal('0'),
                                'days_carry_over': Decimal('0'),
                            }
                        )
                        
                        # Mettre à jour les valeurs
                        balance.days_acquired = data['days_acquired']
                        balance.days_taken = data['days_taken']
                        balance.days_carry_over = data['days_carry_over']
                        balance.save()
                        
                        if created:
                            created_count += 1
                            self.stdout.write(f'   ✅ Créé: {data["username"]} - {data["days_acquired"]}j acquis, {data["days_taken"]}j pris, {data["days_carry_over"]}j reportés')
                        else:
                            updated_count += 1
                            self.stdout.write(f'   🔄 Mis à jour: {data["username"]} - {data["days_acquired"]}j acquis, {data["days_taken"]}j pris, {data["days_carry_over"]}j reportés')
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   ❌ Erreur {data["username"]}: {e}'))
                        raise
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur traitement: {e}'))
            return False
        
        self.stdout.write(self.style.SUCCESS('\n🎉 TRAITEMENT TERMINÉ!'))
        self.stdout.write(f'   📊 Soldes créés: {created_count}')
        self.stdout.write(f'   🔄 Soldes mis à jour: {updated_count}')
        self.stdout.write(f'   📅 Période traitée: {balances_data[0]["period_start"]} → {balances_data[0]["period_end"]}')
        
        return True
