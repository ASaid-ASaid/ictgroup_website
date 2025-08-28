"""
Commande Django pour maintenir les soldes de congés.
Usage: python manage.py optimize_cache
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date
from extranet.models import UserLeaveBalance, UserMonthlyReportCache, get_leave_balance


class Command(BaseCommand):
    help = 'Maintient les soldes de congés et rapports mensuels'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Vide complètement le cache avant de le recalculer',
        )
        parser.add_argument(
            '--users',
            type=str,
            help='Liste des usernames séparés par des virgules (ex: user1,user2)',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Année pour laquelle recalculer le cache',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Affiche les statistiques du cache',
        )
    
    def handle(self, *args, **options):
        if options['stats']:
            self.show_stats()
            return
        
        if options['clear']:
            self.stdout.write('🗑️  Remise à zéro des soldes...')
            # Avec le nouveau système, on peut juste mettre à jour les soldes
            UserMonthlyReportCache.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Cache mensuel vidé'))
        
        # Filtrer les utilisateurs si spécifié
        users = User.objects.filter(is_active=True)
        if options['users']:
            usernames = options['users'].split(',')
            users = users.filter(username__in=usernames)
            self.stdout.write(f'🎯 Utilisateurs sélectionnés: {usernames}')
        
        # Année par défaut
        year = options['year'] or date.today().year
        
        self.stdout.write(f'🔄 Mise à jour des soldes pour {users.count()} utilisateurs...')
        
        # Mise à jour des soldes de congés
        self.update_leave_balances(users, year)
        
        # Pré-calcul des rapports mensuels (6 derniers mois)
        self.precalculate_monthly_reports(users, year)
        
        self.stdout.write(self.style.SUCCESS('✅ Mise à jour terminée'))
        self.show_stats()
    
    def update_leave_balances(self, users, year):
        """Met à jour les soldes de congés pour tous les utilisateurs."""
        self.stdout.write('📊 Mise à jour des soldes de congés...')
        
        for i, user in enumerate(users, 1):
            try:
                # Utiliser get_leave_balance pour créer/mettre à jour le solde
                balance = get_leave_balance(user)
                
                # Affichage du progrès
                if i % 10 == 0 or i == users.count():
                    self.stdout.write(f'   Traité {i}/{users.count()} utilisateurs')
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Erreur pour {user.username}: {e}')
                )
    
    def precalculate_monthly_reports(self, users, year):
        """Pré-calcule les rapports mensuels."""
        self.stdout.write('📈 Calcul des rapports mensuels...')
        
        # Calculer pour les 6 derniers mois
        current_date = date.today()
        months_to_calculate = []
        
        for i in range(6):
            calc_month = current_date.month - i
            calc_year = current_date.year
            
            if calc_month <= 0:
                calc_month += 12
                calc_year -= 1
            
            months_to_calculate.append((calc_year, calc_month))
        
        for calc_year, calc_month in months_to_calculate:
            self.stdout.write(f'   📅 {calc_year}-{calc_month:02d}')
            
            for i, user in enumerate(users, 1):
                try:
                    # Force le recalcul en utilisant le gestionnaire optimisé
                    OptimizedMonthlyReportManager.get_or_calculate_monthly_data(
                        user, calc_year, calc_month
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Erreur rapport {user.username} {calc_year}-{calc_month}: {e}'
                        )
                    )
    
    def show_stats(self):
        """Affiche les statistiques des soldes."""
        balance_count = UserLeaveBalance.objects.count()
        monthly_count = UserMonthlyReportCache.objects.count()
        
        self.stdout.write('\n📊 Statistiques des données:')
        self.stdout.write(f'   💰 Soldes de congés: {balance_count}')
        self.stdout.write(f'   📅 Rapports mensuels en cache: {monthly_count}')
        
        if balance_count > 0:
            recent_balance = UserLeaveBalance.objects.order_by('-last_updated').first()
            self.stdout.write(f'   🕐 Dernière mise à jour solde: {recent_balance.last_updated}')
        
        if monthly_count > 0:
            recent_monthly = UserMonthlyReportCache.objects.order_by('-last_updated').first()
            self.stdout.write(f'   🕐 Dernier calcul mensuel: {recent_monthly.last_updated}')
