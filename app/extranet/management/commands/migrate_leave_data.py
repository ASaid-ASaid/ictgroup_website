"""
Commande Django pour migrer les données de congés de l'ancien système vers le nouveau.
Permet d'importer les soldes de congés existants (acquis, pris, report) pour tous les utilisateurs
à partir d'un fichier CSV ou JSON.

Usage:
    python manage.py migrate_leave_data --file path/to/data.csv
    python manage.py migrate_leave_data --file path/to/data.json
    python manage.py migrate_leave_data --interactive
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from extranet.models import UserLeaveBalance, UserProfile
from datetime import date, datetime
from decimal import Decimal
import csv
import json
import os


class Command(BaseCommand):
    help = 'Migre les données de congés de l\'ancien système vers le nouveau'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Fichier CSV ou JSON contenant les données à migrer'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Mode interactif pour saisir les données manuellement'
        )
        parser.add_argument(
            '--period-start',
            type=str,
            help='Date de début de période (YYYY-MM-DD), par défaut 2024-06-01'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans modification des données'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Écraser les données existantes'
        )

    def handle(self, *args, **options):
        file_path = options.get('file')
        interactive = options.get('interactive')
        period_start_str = options.get('period_start', '2024-06-01')
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        # Parse period_start
        try:
            period_start = datetime.strptime(period_start_str, '%Y-%m-%d').date()
        except ValueError:
            raise CommandError(f"Format de date invalide : {period_start_str}. Utilisez YYYY-MM-DD")

        # Calculer period_end (31 mai de l'année suivante)
        period_end = date(period_start.year + 1, 5, 31)

        self.stdout.write(
            f"Migration des données de congés pour la période : "
            f"{period_start} au {period_end}"
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODE SIMULATION - Aucune donnée ne sera modifiée")
            )

        # Traitement selon le mode
        if interactive:
            self._interactive_migration(period_start, period_end, dry_run, force)
        elif file_path:
            self._file_migration(file_path, period_start, period_end, dry_run, force)
        else:
            raise CommandError("Vous devez spécifier --file ou --interactive")

    def _interactive_migration(self, period_start, period_end, dry_run, force):
        """Mode interactif pour saisir les données utilisateur par utilisateur"""
        
        users = User.objects.filter(is_active=True).order_by('username')
        
        self.stdout.write(f"\n=== Mode interactif - {users.count()} utilisateurs ===")
        self.stdout.write("Appuyez sur Entrée pour ignorer un utilisateur")
        self.stdout.write("Tapez 'quit' pour arrêter\n")

        migrated_count = 0
        skipped_count = 0

        for user in users:
            # Vérifier si l'utilisateur a déjà un solde pour cette période
            existing_balance = UserLeaveBalance.objects.filter(
                user=user,
                period_start=period_start
            ).first()

            if existing_balance and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f"IGNORÉ: {user.username} - Solde existant (utilisez --force pour écraser)"
                    )
                )
                skipped_count += 1
                continue

            # Afficher les infos utilisateur
            try:
                profile = user.profile
                site = profile.site
                role = profile.role
            except:
                site = "tunisie"
                role = "user"

            self.stdout.write(f"\n--- {user.username} ({user.first_name} {user.last_name}) ---")
            self.stdout.write(f"Site: {site} | Rôle: {role}")

            # Saisie des données
            try:
                # Jours acquis
                acquired_input = input("Jours acquis (25.0): ").strip()
                if acquired_input.lower() == 'quit':
                    break
                if not acquired_input:
                    skipped_count += 1
                    continue
                
                days_acquired = Decimal(acquired_input or '25.0')

                # Jours pris
                taken_input = input("Jours pris (0.0): ").strip()
                days_taken = Decimal(taken_input or '0.0')

                # Report de l'année précédente
                carry_input = input("Report année précédente (0.0): ").strip()
                days_carry_over = Decimal(carry_input or '0.0')

                # Afficher le résumé
                total_available = days_acquired + days_carry_over
                remaining = total_available - days_taken

                self.stdout.write(f"Résumé:")
                self.stdout.write(f"  Acquis: {days_acquired}j")
                self.stdout.write(f"  Report: {days_carry_over}j")
                self.stdout.write(f"  Total disponible: {total_available}j")
                self.stdout.write(f"  Pris: {days_taken}j")
                self.stdout.write(f"  Restant: {remaining}j")

                # Confirmation
                confirm = input("Confirmer ? (o/N): ").strip().lower()
                if confirm not in ['o', 'oui', 'y', 'yes']:
                    skipped_count += 1
                    continue

                # Création/mise à jour du solde
                if not dry_run:
                    balance_data = {
                        'user': user,
                        'period_start': period_start,
                        'defaults': {
                            'period_end': period_end,
                            'days_acquired': days_acquired,
                            'days_taken': days_taken,
                            'days_carry_over': days_carry_over,
                        }
                    }

                    balance, created = UserLeaveBalance.objects.update_or_create(**balance_data)
                    
                    action = "CRÉÉ" if created else "MIS À JOUR"
                    self.stdout.write(
                        self.style.SUCCESS(f"{action}: {user.username}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"SIMULATION: {user.username}")
                    )

                migrated_count += 1

            except ValueError as e:
                self.stdout.write(
                    self.style.ERROR(f"Erreur de saisie pour {user.username}: {e}")
                )
                skipped_count += 1
                continue
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\nInterruption utilisateur"))
                break

        # Résumé final
        self.stdout.write(f"\n=== Résumé migration ===")
        self.stdout.write(f"Migrés: {migrated_count}")
        self.stdout.write(f"Ignorés: {skipped_count}")

    def _file_migration(self, file_path, period_start, period_end, dry_run, force):
        """Migration à partir d'un fichier CSV ou JSON"""
        
        if not os.path.exists(file_path):
            raise CommandError(f"Fichier introuvable : {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            data = self._parse_csv(file_path)
        elif file_ext == '.json':
            data = self._parse_json(file_path)
        else:
            raise CommandError("Format de fichier non supporté. Utilisez CSV ou JSON")

        self.stdout.write(f"Données chargées : {len(data)} entrées")

        migrated_count = 0
        error_count = 0
        skipped_count = 0

        for entry in data:
            try:
                username = entry.get('username', '').strip()
                if not username:
                    self.stdout.write(self.style.ERROR("Nom d'utilisateur manquant"))
                    error_count += 1
                    continue

                # Trouver l'utilisateur
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Utilisateur introuvable : {username}")
                    )
                    error_count += 1
                    continue

                # Vérifier si l'utilisateur a déjà un solde
                existing_balance = UserLeaveBalance.objects.filter(
                    user=user,
                    period_start=period_start
                ).first()

                if existing_balance and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f"IGNORÉ: {username} - Solde existant"
                        )
                    )
                    skipped_count += 1
                    continue

                # Parser les valeurs
                days_acquired = Decimal(str(entry.get('days_acquired', 25.0)))
                days_taken = Decimal(str(entry.get('days_taken', 0.0)))
                days_carry_over = Decimal(str(entry.get('days_carry_over', 0.0)))

                # Validation des valeurs
                if days_acquired < 0 or days_taken < 0 or days_carry_over < 0:
                    self.stdout.write(
                        self.style.ERROR(f"Valeurs négatives pour {username}")
                    )
                    error_count += 1
                    continue

                # Création/mise à jour
                if not dry_run:
                    balance_data = {
                        'user': user,
                        'period_start': period_start,
                        'defaults': {
                            'period_end': period_end,
                            'days_acquired': days_acquired,
                            'days_taken': days_taken,
                            'days_carry_over': days_carry_over,
                        }
                    }

                    balance, created = UserLeaveBalance.objects.update_or_create(**balance_data)
                    
                    action = "CRÉÉ" if created else "MIS À JOUR"
                    remaining = balance.days_remaining
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{action}: {username} - Restant: {remaining}j"
                        )
                    )
                else:
                    remaining = days_acquired + days_carry_over - days_taken
                    self.stdout.write(
                        self.style.WARNING(
                            f"SIMULATION: {username} - Restant: {remaining}j"
                        )
                    )

                migrated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erreur pour {entry.get('username', 'INCONNU')}: {e}")
                )
                error_count += 1

        # Résumé final
        self.stdout.write(f"\n=== Résumé migration fichier ===")
        self.stdout.write(f"Migrés: {migrated_count}")
        self.stdout.write(f"Ignorés: {skipped_count}")
        self.stdout.write(f"Erreurs: {error_count}")

    def _parse_csv(self, file_path):
        """Parse un fichier CSV avec les colonnes : username,days_acquired,days_taken,days_carry_over"""
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Détecter automatiquement le délimiteur
            sample = csvfile.read(1024)
            csvfile.seek(0)
            delimiter = ',' if ',' in sample else ';'
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            expected_fields = ['username', 'days_acquired', 'days_taken', 'days_carry_over']
            
            # Vérifier les colonnes
            if not all(field in reader.fieldnames for field in expected_fields):
                raise CommandError(
                    f"Colonnes manquantes dans le CSV. Attendues: {expected_fields}. "
                    f"Trouvées: {reader.fieldnames}"
                )
            
            for row in reader:
                data.append(row)
        
        return data

    def _parse_json(self, file_path):
        """Parse un fichier JSON avec un array d'objets"""
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
        
        if not isinstance(data, list):
            raise CommandError("Le fichier JSON doit contenir un array d'objets")
        
        return data

    def _create_template_files(self):
        """Crée des fichiers templates pour l'import"""
        # Template CSV
        csv_template = """username,days_acquired,days_taken,days_carry_over
ASaid,25.0,5.0,2.5
NBenz,25.0,0.0,0.0
FHmai,25.0,10.0,1.0"""

        # Template JSON
        json_template = [
            {
                "username": "ASaid",
                "days_acquired": 25.0,
                "days_taken": 5.0,
                "days_carry_over": 2.5
            },
            {
                "username": "NBenz", 
                "days_acquired": 25.0,
                "days_taken": 0.0,
                "days_carry_over": 0.0
            }
        ]

        self.stdout.write("=== Templates de fichiers ===")
        self.stdout.write("\nCSV Template:")
        self.stdout.write(csv_template)
        self.stdout.write("\nJSON Template:")
        self.stdout.write(json.dumps(json_template, indent=2))
