#!/usr/bin/env python
"""
Module de tests de performance pour l'application ICTGroup Website.

Ce module teste les performances des vues, requêtes de base de données,
et temps de réponse des différentes pages de l'extranet.

Usage:
    python performance_tests.py
    
Note: Ce fichier n'est pas versionné dans Git (.gitignore)
"""

import os
import sys
import time
import json
import requests
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration Django pour les tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ictgroup.settings')

try:
    import django
    django.setup()
    
    from django.test import Client
    from django.contrib.auth.models import User
    from django.db import connection
    from extranet.models import LeaveRequest, TeleworkRequest, UserProfile, StockItem
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("⚠️  Django non disponible - tests HTTP seulement")

class PerformanceMonitor:
    """Moniteur de performance pour l'application."""
    
    def __init__(self):
        self.results = []
        self.base_url = "http://localhost:8000"
        self.client = Client() if DJANGO_AVAILABLE else None
        
    def log_result(self, test_name, duration, status="SUCCESS", details=None):
        """Enregistre un résultat de test."""
        result = {
            'test': test_name,
            'duration_ms': round(duration * 1000, 2),
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        
        # Affichage coloré
        color = "🟢" if status == "SUCCESS" else "🔴" if status == "ERROR" else "🟡"
        print(f"{color} {test_name}: {result['duration_ms']}ms")
        
    def time_function(self, func, *args, **kwargs):
        """Mesure le temps d'exécution d'une fonction."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            return result, duration, None
        except Exception as e:
            duration = time.time() - start_time
            return None, duration, str(e)

class DatabasePerformanceTests(PerformanceMonitor):
    """Tests de performance de la base de données."""
    
    def test_query_performance(self):
        """Teste les performances des requêtes principales."""
        if not DJANGO_AVAILABLE:
            return
            
        print("\n📊 Tests de performance Base de Données")
        print("=" * 50)
        
        # Test 1: Comptage des utilisateurs
        result, duration, error = self.time_function(User.objects.count)
        if error:
            self.log_result("DB: Count Users", duration, "ERROR", {"error": error})
        else:
            self.log_result("DB: Count Users", duration, "SUCCESS", {"count": result})
        
        # Test 2: Requête avec JOIN (UserProfile)
        result, duration, error = self.time_function(
            lambda: list(UserProfile.objects.select_related('user').all()[:10])
        )
        if error:
            self.log_result("DB: UserProfile JOIN", duration, "ERROR", {"error": error})
        else:
            self.log_result("DB: UserProfile JOIN", duration, "SUCCESS", {"count": len(result)})
        
        # Test 3: Requêtes de congés
        result, duration, error = self.time_function(
            lambda: list(LeaveRequest.objects.select_related('user').all()[:10])
        )
        if error:
            self.log_result("DB: LeaveRequest Query", duration, "ERROR", {"error": error})
        else:
            self.log_result("DB: LeaveRequest Query", duration, "SUCCESS", {"count": len(result)})
        
        # Test 4: Analyse des requêtes SQL
        self.analyze_sql_queries()
    
    def analyze_sql_queries(self):
        """Analyse le nombre de requêtes SQL générées."""
        if not DJANGO_AVAILABLE:
            return
            
        from django.db import reset_queries
        from django.conf import settings
        
        # Activer le debug temporairement
        old_debug = settings.DEBUG
        settings.DEBUG = True
        
        reset_queries()
        start_time = time.time()
        
        try:
            # Simulation d'une page complexe
            users = list(User.objects.select_related('profile').all()[:5])
            for user in users:
                LeaveRequest.objects.filter(user=user).count()
                TeleworkRequest.objects.filter(user=user).count()
            
            duration = time.time() - start_time
            query_count = len(connection.queries)
            
            self.log_result(
                "DB: Complex Page Simulation", 
                duration, 
                "SUCCESS", 
                {"sql_queries": query_count, "users_processed": len(users)}
            )
            
        finally:
            settings.DEBUG = old_debug

class WebPerformanceTests(PerformanceMonitor):
    """Tests de performance des pages web."""
    
    def test_page_load_times(self):
        """Teste les temps de chargement des pages principales."""
        print("\n🌐 Tests de performance Web")
        print("=" * 50)
        
        # Pages à tester
        pages = [
            ("/extranet/", "Page d'accueil extranet"),
            ("/extranet/utilisateurs/", "Gestion utilisateurs"),
            ("/extranet/demandes/", "Liste des demandes"),
            ("/extranet/calendrier/", "Calendrier"),
            ("/extranet/magasin/stock/", "Gestion stock"),
            ("/extranet/admin/conges/", "Admin congés"),
            ("/extranet/admin/teletravail/", "Admin télétravail"),
        ]
        
        for url, description in pages:
            self.test_single_page(url, description)
    
    def test_single_page(self, url, description):
        """Teste une page individuelle."""
        if DJANGO_AVAILABLE and self.client:
            # Test avec client Django (plus précis)
            result, duration, error = self.time_function(self.client.get, url)
            
            if error:
                self.log_result(f"Web: {description}", duration, "ERROR", {"error": error})
            else:
                status = "SUCCESS" if result.status_code < 400 else "WARNING"
                self.log_result(
                    f"Web: {description}", 
                    duration, 
                    status, 
                    {"status_code": result.status_code}
                )
        else:
            # Test avec requests HTTP
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{url}", timeout=10)
                duration = time.time() - start_time
                
                status = "SUCCESS" if response.status_code < 400 else "WARNING"
                self.log_result(
                    f"HTTP: {description}", 
                    duration, 
                    status, 
                    {"status_code": response.status_code}
                )
            except requests.RequestException as e:
                duration = time.time() - start_time
                self.log_result(f"HTTP: {description}", duration, "ERROR", {"error": str(e)})

class LoadTests(PerformanceMonitor):
    """Tests de charge pour évaluer la capacité de l'application."""
    
    def test_concurrent_requests(self, num_threads=5, num_requests=20):
        """Teste les requêtes simultanées."""
        print(f"\n⚡ Tests de charge ({num_threads} threads, {num_requests} requêtes)")
        print("=" * 50)
        
        url = f"{self.base_url}/extranet/"
        durations = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                return duration, response.status_code, None
            except Exception as e:
                duration = time.time() - start_time
                return duration, 0, str(e)
        
        start_total = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                duration, status_code, error = future.result()
                durations.append(duration)
                if error:
                    errors.append(error)
        
        total_duration = time.time() - start_total
        
        if durations:
            self.log_result(
                "Load: Concurrent Requests",
                statistics.mean(durations),
                "SUCCESS" if len(errors) == 0 else "WARNING",
                {
                    "total_requests": num_requests,
                    "errors": len(errors),
                    "avg_response_time": round(statistics.mean(durations) * 1000, 2),
                    "min_response_time": round(min(durations) * 1000, 2),
                    "max_response_time": round(max(durations) * 1000, 2),
                    "total_duration": round(total_duration, 2),
                    "requests_per_second": round(num_requests / total_duration, 2)
                }
            )

class PerformanceReporter:
    """Générateur de rapports de performance."""
    
    def __init__(self, results):
        self.results = results
    
    def generate_summary(self):
        """Génère un résumé des performances."""
        print("\n📈 Résumé des performances")
        print("=" * 50)
        
        success_tests = [r for r in self.results if r['status'] == 'SUCCESS']
        warning_tests = [r for r in self.results if r['status'] == 'WARNING']
        error_tests = [r for r in self.results if r['status'] == 'ERROR']
        
        print(f"✅ Tests réussis: {len(success_tests)}")
        print(f"⚠️  Tests avec avertissements: {len(warning_tests)}")
        print(f"❌ Tests en erreur: {len(error_tests)}")
        print(f"📊 Total des tests: {len(self.results)}")
        
        if success_tests:
            durations = [r['duration_ms'] for r in success_tests]
            print(f"\n⏱️  Temps de réponse (tests réussis):")
            print(f"   Moyenne: {statistics.mean(durations):.2f}ms")
            print(f"   Médiane: {statistics.median(durations):.2f}ms")
            print(f"   Min: {min(durations):.2f}ms")
            print(f"   Max: {max(durations):.2f}ms")
        
        # Tests les plus lents
        slow_tests = sorted(self.results, key=lambda x: x['duration_ms'], reverse=True)[:5]
        print(f"\n🐌 Tests les plus lents:")
        for test in slow_tests:
            print(f"   {test['test']}: {test['duration_ms']}ms")
    
    def save_detailed_report(self, filename=None):
        """Sauvegarde un rapport détaillé."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "success": len([r for r in self.results if r['status'] == 'SUCCESS']),
                "warnings": len([r for r in self.results if r['status'] == 'WARNING']),
                "errors": len([r for r in self.results if r['status'] == 'ERROR'])
            },
            "tests": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport détaillé sauvegardé: {filename}")

def main():
    """Fonction principale d'exécution des tests."""
    print("🚀 Tests de performance ICTGroup Website")
    print("=" * 60)
    print(f"📅 Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Tests de base de données
    if DJANGO_AVAILABLE:
        db_tests = DatabasePerformanceTests()
        db_tests.test_query_performance()
        all_results.extend(db_tests.results)
    
    # Tests web
    web_tests = WebPerformanceTests()
    web_tests.test_page_load_times()
    all_results.extend(web_tests.results)
    
    # Tests de charge
    load_tests = LoadTests()
    load_tests.test_concurrent_requests(num_threads=3, num_requests=10)
    all_results.extend(load_tests.results)
    
    # Génération du rapport
    reporter = PerformanceReporter(all_results)
    reporter.generate_summary()
    reporter.save_detailed_report()
    
    print(f"\n✅ Tests terminés: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
