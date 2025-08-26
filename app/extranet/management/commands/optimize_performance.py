"""
Commande Django pour optimiser les performances du système.
Usage: python manage.py optimize_performance [options]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
from datetime import date
import time


class Command(BaseCommand):
    help = 'Optimise les performances du système : cache, base de données, statistiques'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--warm-cache',
            action='store_true',
            help='Préchauffe le cache avec les données critiques',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Vide complètement le cache',
        )
        parser.add_argument(
            '--update-stats',
            action='store_true',
            help='Met à jour les statistiques mensuelles de tous les utilisateurs',
        )
        parser.add_argument(
            '--analyze-db',
            action='store_true',
            help='Analyse les performances de la base de données',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Exécute toutes les optimisations',
        )
        parser.add_argument(
            '--users',
            type=str,
            help='Liste des usernames séparés par des virgules (ex: user1,user2)',
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        self.stdout.write('🚀 Optimisation des performances en cours...\n')
        
        if options['all']:
            options['clear_cache'] = True
            options['warm_cache'] = True
            options['update_stats'] = True
            options['analyze_db'] = True
        
        # Filtrer les utilisateurs si spécifié
        users = User.objects.filter(is_active=True).select_related('profile')
        if options['users']:
            usernames = options['users'].split(',')
            users = users.filter(username__in=usernames)
            self.stdout.write(f'🎯 Utilisateurs sélectionnés: {usernames}')
        
        # 1. Nettoyage du cache
        if options['clear_cache']:
            self.clear_cache()
        
        # 2. Analyse de la base de données
        if options['analyze_db']:
            self.analyze_database()
        
        # 3. Mise à jour des statistiques
        if options['update_stats']:
            self.update_statistics(users)
        
        # 4. Réchauffement du cache
        if options['warm_cache']:
            self.warm_cache(users)
        
        duration = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Optimisation terminée en {duration:.2f}s'
            )
        )

    def clear_cache(self):
        """Vide le cache Redis"""
        self.stdout.write('🗑️  Nettoyage du cache...')
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✅ Cache vidé'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Cache non disponible: {e}'))

    def warm_cache(self, users):
        """Préchauffe le cache avec les données critiques"""
        self.stdout.write(f'🔥 Préchauffage du cache pour {users.count()} utilisateurs...')
        
        try:
            from extranet.utils import warm_up_cache
            warm_up_cache()
            self.stdout.write(self.style.SUCCESS('✅ Cache préchauffé'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Erreur lors du préchauffage: {e}'))

    def update_statistics(self, users):
        """Met à jour les statistiques mensuelles"""
        self.stdout.write(f'📊 Mise à jour des statistiques pour {users.count()} utilisateurs...')
        
        try:
            from extranet.models import MonthlyUserStats
            from extranet.utils import batch_update_user_stats
            
            current_date = date.today()
            
            # Mettre à jour le mois courant et le précédent
            for month_offset in [0, -1]:
                target_date = current_date.replace(day=1)
                if month_offset == -1:
                    if target_date.month == 1:
                        target_date = target_date.replace(year=target_date.year - 1, month=12)
                    else:
                        target_date = target_date.replace(month=target_date.month - 1)
                
                batch_update_user_stats(users, target_date.year, target_date.month)
                self.stdout.write(f'   ✓ Mois {target_date.year}-{target_date.month:02d} mis à jour')
            
            self.stdout.write(self.style.SUCCESS('✅ Statistiques mises à jour'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la mise à jour: {e}'))

    def analyze_database(self):
        """Analyse les performances de la base de données"""
        self.stdout.write('🔍 Analyse de la base de données...')
        
        try:
            with connection.cursor() as cursor:
                # Statistiques des tables principales
                tables = [
                    'extranet_leaverequest',
                    'extranet_teleworkrequest', 
                    'extranet_overtimerequest',
                    'extranet_userleavebalance',
                    'extranet_monthlyuserstats',
                    'auth_user'
                ]
                
                self.stdout.write('\n📋 Statistiques des tables:')
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        self.stdout.write(f'   {table}: {count:,} enregistrements')
                    except Exception as e:
                        self.stdout.write(f'   {table}: Erreur - {e}')
                
                # Index manquants potentiels
                self.stdout.write('\n🔍 Vérification des index:')
                self.check_missing_indexes(cursor)
                
                # Requêtes lentes potentielles
                self.stdout.write('\n⚠️  Suggestions d\'optimisation:')
                self.suggest_optimizations()
                
            self.stdout.write(self.style.SUCCESS('✅ Analyse terminée'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de l\'analyse: {e}'))

    def check_missing_indexes(self, cursor):
        """Vérifie les index manquants"""
        # Vérifications spécifiques PostgreSQL
        try:
            # Index sur les colonnes de filtrage fréquent
            important_indexes = [
                ('extranet_leaverequest', 'user_id', 'status'),
                ('extranet_leaverequest', 'start_date', 'end_date'),
                ('extranet_teleworkrequest', 'user_id', 'status'),
                ('extranet_overtimerequest', 'user_id', 'status'),
                ('extranet_userleavebalance', 'user_id', 'period_start'),
                ('extranet_monthlyuserstats', 'user_id', 'year', 'month'),
            ]
            
            for table, *columns in important_indexes:
                index_name = f"idx_{table}_{'_'.join(columns)}"
                cursor.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = %s AND indexname = %s
                """, [table, index_name])
                
                if cursor.fetchone():
                    self.stdout.write(f'   ✓ Index {index_name} présent')
                else:
                    self.stdout.write(f'   ⚠️  Index {index_name} manquant')
                    
        except Exception as e:
            self.stdout.write(f'   ❌ Erreur vérification index: {e}')

    def suggest_optimizations(self):
        """Suggère des optimisations"""
        suggestions = [
            "Utiliser select_related() pour les requêtes avec jointures",
            "Utiliser prefetch_related() pour les relationsMany-to-Many",
            "Mettre en cache les calculs de soldes de congés",
            "Paginer les grandes listes de demandes",
            "Optimiser les requêtes de tableau de bord",
            "Utiliser des index composites pour les filtres multiples",
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            self.stdout.write(f'   {i}. {suggestion}')

    def show_cache_stats(self):
        """Affiche les statistiques du cache"""
        try:
            # Tentative de récupération des stats Redis
            self.stdout.write('\n📊 Statistiques du cache:')
            
            # Test de connectivité
            cache.set('test_key', 'test_value', 10)
            if cache.get('test_key') == 'test_value':
                self.stdout.write('   ✓ Cache Redis opérationnel')
                cache.delete('test_key')
            else:
                self.stdout.write('   ❌ Cache Redis non accessible')
            
        except Exception as e:
            self.stdout.write(f'   ❌ Erreur cache: {e}')
