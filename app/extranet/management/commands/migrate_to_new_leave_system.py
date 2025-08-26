"""
Commande Django pour migrer les données vers le nouveau système de gestion des congés.
Usage: python manage.py migrate_to_new_leave_system
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from extranet.models import UserLeaveBalance, MonthlyUserStats, get_leave_balance


class Command(BaseCommand):
    help = "Migre les données vers le nouveau système de gestion des congés et statistiques"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=str,
            help="Liste des usernames séparés par des virgules (ex: user1,user2)",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Année spécifique à traiter (par défaut: année courante)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule l'opération sans modifier les données",
        )
        parser.add_argument(
            "--recalculate",
            action="store_true",
            help="Recalcule toutes les données existantes",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("Mode simulation activé - aucune modification ne sera apportée")
            )

        # Déterminer les utilisateurs à traiter
        if options["users"]:
            usernames = [u.strip() for u in options["users"].split(",")]
            users = User.objects.filter(username__in=usernames)
            missing_users = set(usernames) - set(users.values_list("username", flat=True))
            if missing_users:
                self.stdout.write(
                    self.style.ERROR(f"Utilisateurs non trouvés: {', '.join(missing_users)}")
                )
                return
        else:
            users = User.objects.filter(is_active=True)

        # Déterminer l'année à traiter
        target_year = options["year"] or date.today().year

        self.stdout.write(
            self.style.SUCCESS(
                f"Traitement de {users.count()} utilisateur(s) pour l'année {target_year}"
            )
        )

        # Statistiques
        stats = {
            "balances_created": 0,
            "balances_updated": 0,
            "monthly_stats_created": 0,
            "monthly_stats_updated": 0,
            "errors": 0,
        }

        for user in users:
            try:
                self.stdout.write(f"Traitement de {user.username}...")
                
                # Créer/mettre à jour le solde de congés
                self._process_user_balance(user, target_year, stats)
                
                # Créer/mettre à jour les statistiques mensuelles
                self._process_monthly_stats(user, target_year, stats)
                
            except Exception as e:
                stats["errors"] += 1
                self.stdout.write(
                    self.style.ERROR(f"Erreur pour {user.username}: {e}")
                )

        # Afficher le résumé
        self._print_summary(stats)

    def _process_user_balance(self, user, year, stats):
        """Traite le solde de congés d'un utilisateur pour l'année donnée."""
        
        # Déterminer la période de congés
        if date.today().month >= 6:
            period_start = date(year, 6, 1)
        else:
            period_start = date(year - 1, 6, 1)
        
        try:
            balance = UserLeaveBalance.objects.get(
                user=user,
                period_start=period_start
            )
            
            if not self.dry_run:
                balance.update_taken_days()
            
            stats["balances_updated"] += 1
            self.stdout.write(f"  ✓ Solde mis à jour pour {user.username}")
            
        except UserLeaveBalance.DoesNotExist:
            # Créer automatiquement via get_leave_balance
            if not self.dry_run:
                balance_info = get_leave_balance(user)
                self.stdout.write(
                    f"  ✓ Solde créé: {balance_info['remaining']} jours restants"
                )
            
            stats["balances_created"] += 1

    def _process_monthly_stats(self, user, year, stats):
        """Traite les statistiques mensuelles d'un utilisateur pour l'année donnée."""
        
        for month in range(1, 13):
            try:
                stats_obj, created = MonthlyUserStats.objects.get_or_create(
                    user=user,
                    year=year,
                    month=month
                )
                
                if not self.dry_run:
                    stats_obj.update_from_requests()
                
                if created:
                    stats["monthly_stats_created"] += 1
                else:
                    stats["monthly_stats_updated"] += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Erreur statistiques {year}/{month:02d} pour {user.username}: {e}"
                    )
                )

    def _print_summary(self, stats):
        """Affiche le résumé des opérations."""
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("RÉSUMÉ DES OPÉRATIONS"))
        self.stdout.write("="*50)
        
        self.stdout.write(f"Soldes de congés créés: {stats['balances_created']}")
        self.stdout.write(f"Soldes de congés mis à jour: {stats['balances_updated']}")
        self.stdout.write(f"Statistiques mensuelles créées: {stats['monthly_stats_created']}")
        self.stdout.write(f"Statistiques mensuelles mises à jour: {stats['monthly_stats_updated']}")
        
        if stats["errors"] > 0:
            self.stdout.write(
                self.style.ERROR(f"Erreurs rencontrées: {stats['errors']}")
            )
        else:
            self.stdout.write(self.style.SUCCESS("✓ Aucune erreur rencontrée"))
            
        total_operations = (
            stats["balances_created"] + 
            stats["balances_updated"] + 
            stats["monthly_stats_created"] + 
            stats["monthly_stats_updated"]
        )
        
        self.stdout.write(f"\nTotal des opérations: {total_operations}")
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠ Mode simulation - Exécutez sans --dry-run pour appliquer les changements"
                )
            )
