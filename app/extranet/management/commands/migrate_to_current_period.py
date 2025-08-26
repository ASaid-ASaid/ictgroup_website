"""
Commande Django pour copier les soldes de congés de la période précédente vers la période courante.
Utilise les reports automatiques et met à jour les acquis pour la nouvelle période.

Usage:
    python manage.py migrate_to_current_period
    python manage.py migrate_to_current_period --from-period 2024-06-01
    python manage.py migrate_to_current_period --dry-run
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from extranet.models import UserLeaveBalance, get_leave_balance
from datetime import date, datetime
from decimal import Decimal


class Command(BaseCommand):
    help = 'Migre les soldes de congés vers la période courante avec reports automatiques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-period',
            type=str,
            help='Date de début de la période source (YYYY-MM-DD), par défaut période précédente'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans modification des données'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Écraser les données existantes de la période courante'
        )

    def handle(self, *args, **options):
        from_period_str = options.get('from_period')
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        # Déterminer les périodes
        today = date.today()
        
        # Période courante
        if today.month >= 6:
            current_period_start = date(today.year, 6, 1)
        else:
            current_period_start = date(today.year - 1, 6, 1)
        current_period_end = date(current_period_start.year + 1, 5, 31)

        # Période source
        if from_period_str:
            try:
                source_period_start = datetime.strptime(from_period_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f"Format de date invalide : {from_period_str}")
                )
                return
        else:
            # Période précédente (une année avant la courante)
            source_period_start = date(current_period_start.year - 1, 6, 1)
        
        source_period_end = date(source_period_start.year + 1, 5, 31)

        self.stdout.write(f"Migration des soldes de congés :")
        self.stdout.write(f"  Période source : {source_period_start} au {source_period_end}")
        self.stdout.write(f"  Période cible  : {current_period_start} au {current_period_end}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODE SIMULATION - Aucune donnée ne sera modifiée")
            )

        # Récupérer tous les utilisateurs avec un solde dans la période source
        source_balances = UserLeaveBalance.objects.filter(
            period_start=source_period_start
        ).select_related('user')

        if not source_balances.exists():
            self.stdout.write(
                self.style.ERROR(f"Aucun solde trouvé pour la période source {source_period_start}")
            )
            return

        self.stdout.write(f"Trouvé {source_balances.count()} soldes à migrer")

        migrated_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for source_balance in source_balances:
            try:
                user = source_balance.user
                
                # Vérifier si l'utilisateur a déjà un solde pour la période courante
                existing_balance = UserLeaveBalance.objects.filter(
                    user=user,
                    period_start=current_period_start
                ).first()

                if existing_balance and not force:
                    self.stdout.write(
                        f"IGNORÉ: {user.username} - Solde existant pour période courante"
                    )
                    skipped_count += 1
                    continue

                # Calculer les valeurs pour la nouvelle période
                # Report = jours restants de la période précédente (avec limite)
                remaining_from_previous = source_balance.days_remaining
                max_carry_over = Decimal('5.0')  # Limite de report par défaut
                carry_over = min(remaining_from_previous, max_carry_over) if remaining_from_previous > 0 else Decimal('0.0')

                # Jours acquis pour la nouvelle période (calculé automatiquement)
                from extranet.models import _calculate_acquired_days_new
                days_acquired = _calculate_acquired_days_new(user, current_period_start, current_period_end)

                # Résumé pour l'utilisateur
                total_available = days_acquired + carry_over
                
                self.stdout.write(f"\n--- {user.username} ---")
                self.stdout.write(f"  Période précédente : {source_balance.days_remaining}j restants")
                self.stdout.write(f"  Report autorisé    : {carry_over}j")
                self.stdout.write(f"  Nouveaux acquis    : {days_acquired}j")
                self.stdout.write(f"  Total disponible   : {total_available}j")

                if not dry_run:
                    # Créer ou mettre à jour le solde pour la période courante
                    balance_data = {
                        'user': user,
                        'period_start': current_period_start,
                        'defaults': {
                            'period_end': current_period_end,
                            'days_acquired': days_acquired,
                            'days_taken': Decimal('0.0'),
                            'days_carry_over': carry_over,
                        }
                    }

                    if existing_balance:
                        # Mise à jour
                        existing_balance.days_acquired = days_acquired
                        existing_balance.days_carry_over = carry_over
                        existing_balance.days_taken = Decimal('0.0')  # Reset pour nouvelle période
                        existing_balance.save()
                        
                        self.stdout.write(
                            self.style.WARNING(f"MIS À JOUR: {user.username}")
                        )
                        updated_count += 1
                    else:
                        # Création
                        new_balance = UserLeaveBalance.objects.create(
                            user=user,
                            period_start=current_period_start,
                            period_end=current_period_end,
                            days_acquired=days_acquired,
                            days_taken=Decimal('0.0'),
                            days_carry_over=carry_over,
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"CRÉÉ: {user.username}")
                        )
                        migrated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"SIMULATION: {user.username}")
                    )
                    migrated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erreur pour {user.username}: {e}")
                )
                error_count += 1

        # Résumé final
        self.stdout.write(f"\n=== Résumé migration période ===")
        self.stdout.write(f"Créés : {migrated_count}")
        self.stdout.write(f"Mis à jour : {updated_count}")
        self.stdout.write(f"Ignorés : {skipped_count}")
        self.stdout.write(f"Erreurs : {error_count}")

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Migration terminée ! Les utilisateurs peuvent maintenant utiliser "
                    f"leurs nouveaux soldes pour la période {current_period_start.year}/{current_period_start.year+1}"
                )
            )
