"""
Commande Django pour mettre à jour les statistiques d'heures supplémentaires.
Utile pour la maintenance et les corrections de données.

Usage:
    python manage.py update_overtime_stats
    python manage.py update_overtime_stats --user username
    python manage.py update_overtime_stats --month 8 --year 2025
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from extranet.models import MonthlyUserStats, OverTimeRequest
from datetime import date
import calendar


class Command(BaseCommand):
    help = 'Met à jour les statistiques d\'heures supplémentaires'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Nom d\'utilisateur spécifique à mettre à jour'
        )
        parser.add_argument(
            '--month',
            type=int,
            help='Mois à mettre à jour (1-12)'
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Année à mettre à jour'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Mettre à jour toutes les statistiques existantes'
        )

    def handle(self, *args, **options):
        user_filter = options.get('user')
        month = options.get('month')
        year = options.get('year')
        update_all = options.get('all')

        # Déterminer la période par défaut (mois courant)
        today = date.today()
        target_year = year or today.year
        target_month = month or today.month

        self.stdout.write(f"Mise à jour des statistiques d'heures supplémentaires...")

        if update_all:
            # Mettre à jour toutes les statistiques existantes
            stats = MonthlyUserStats.objects.all()
            self.stdout.write(f"Mise à jour de {stats.count()} entrées de statistiques...")
            
            for stat in stats:
                old_hours = stat.overtime_hours
                stat.update_from_requests()
                if stat.overtime_hours != old_hours:
                    self.stdout.write(
                        f"  {stat.user.username} {stat.year}-{stat.month:02d}: "
                        f"{old_hours}h → {stat.overtime_hours}h"
                    )
            
            self.stdout.write(
                self.style.SUCCESS("Toutes les statistiques ont été mises à jour")
            )
            return

        # Filtrer les utilisateurs
        users = User.objects.all()
        if user_filter:
            try:
                users = users.filter(username=user_filter)
                if not users.exists():
                    self.stdout.write(
                        self.style.ERROR(f"Utilisateur '{user_filter}' introuvable")
                    )
                    return
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Utilisateur '{user_filter}' introuvable")
                )
                return

        # Mettre à jour pour chaque utilisateur
        for user in users:
            # Créer ou mettre à jour les statistiques
            stats, created = MonthlyUserStats.objects.get_or_create(
                user=user,
                year=target_year,
                month=target_month
            )
            
            old_hours = stats.overtime_hours
            stats.update_from_requests()
            
            if created:
                self.stdout.write(
                    f"Créé: {user.username} {target_year}-{target_month:02d}: {stats.overtime_hours}h"
                )
            elif stats.overtime_hours != old_hours:
                self.stdout.write(
                    f"Mis à jour: {user.username} {target_year}-{target_month:02d}: "
                    f"{old_hours}h → {stats.overtime_hours}h"
                )
            else:
                self.stdout.write(
                    f"Aucun changement: {user.username} {target_year}-{target_month:02d}: {stats.overtime_hours}h"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Statistiques d'heures supplémentaires mises à jour pour "
                f"{target_year}-{target_month:02d}"
            )
        )

        # Afficher un résumé des heures supplémentaires
        self.stdout.write("\n=== Résumé des heures supplémentaires ===")
        
        overtime_requests = OverTimeRequest.objects.filter(
            work_date__year=target_year,
            work_date__month=target_month,
            status='approved'
        )
        
        if user_filter:
            overtime_requests = overtime_requests.filter(user__username=user_filter)
        
        total_hours = sum(req.hours for req in overtime_requests)
        total_requests = overtime_requests.count()
        
        self.stdout.write(f"Période: {target_year}-{target_month:02d}")
        self.stdout.write(f"Total demandes approuvées: {total_requests}")
        self.stdout.write(f"Total heures supplémentaires: {total_hours}h")
        
        if overtime_requests.exists():
            self.stdout.write("\nDétail par utilisateur:")
            user_totals = {}
            for req in overtime_requests:
                username = req.user.username
                if username not in user_totals:
                    user_totals[username] = 0
                user_totals[username] += req.hours
            
            for username, hours in sorted(user_totals.items()):
                self.stdout.write(f"  {username}: {hours}h")
