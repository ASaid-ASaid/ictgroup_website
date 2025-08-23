#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du projet ICTGROUP Website
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Configuration des couleurs
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def log_info(message):
    print(f"{GREEN}[INFO]{NC} {message}")


def log_warn(message):
    print(f"{YELLOW}[WARN]{NC} {message}")


def log_error(message):
    print(f"{RED}[ERROR]{NC} {message}")


def log_success(message):
    print(f"{GREEN}[SUCCESS]{NC} {message}")


def log_header(message):
    print(f"\n{BLUE}=== {message} ==={NC}")


def run_command(command, description):
    """Exécute une commande et retourne le résultat"""
    log_info(f"Exécution: {description}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            log_success(f"✅ {description} - Réussi")
            return True, result.stdout
        else:
            log_error(f"❌ {description} - Échec")
            log_error(f"Erreur: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        log_error(f"❌ {description} - Exception: {str(e)}")
        return False, str(e)


def check_django_setup():
    """Vérifie que Django est correctement configuré"""
    log_header("Vérification de l'environnement Django")

    # Vérifier que manage.py existe
    manage_py = Path(__file__).parent.parent / "app" / "manage.py"
    if not manage_py.exists():
        log_error("manage.py non trouvé dans le dossier app/")
        return False

    # Tester la configuration Django
    success, output = run_command(
        "cd app && python manage.py check --deploy",
        "Vérification de la configuration Django",
    )

    return success


def run_unit_tests():
    """Exécute les tests unitaires Django"""
    log_header("Tests Unitaires Django")

    # Tests des modèles
    success1, _ = run_command(
        "cd app && python manage.py test extranet.tests.test_models --verbosity=2",
        "Tests des modèles",
    )

    # Tests des vues
    success2, _ = run_command(
        "cd app && python manage.py test extranet.tests.test_views --verbosity=2",
        "Tests des vues",
    )

    # Tests des formulaires
    success3, _ = run_command(
        "cd app && python manage.py test extranet.tests.test_forms --verbosity=2",
        "Tests des formulaires",
    )

    # Tests d'authentification
    success4, _ = run_command(
        "cd app && python manage.py test extranet.tests.test_auth --verbosity=2",
        "Tests d'authentification",
    )

    return all([success1, success2, success3, success4])


def run_custom_tests():
    """Exécute les tests personnalisés du dossier tests/"""
    log_header("Tests Personnalisés")

    tests_dir = Path(__file__).parent
    test_files = ["test_models.py", "test_views.py", "test_forms.py", "test_auth.py"]

    results = []
    for test_file in test_files:
        test_path = tests_dir / test_file
        if test_path.exists():
            success, _ = run_command(
                f"python {test_path}", f"Test personnalisé: {test_file}"
            )
            results.append(success)
        else:
            log_warn(f"Fichier de test non trouvé: {test_file}")

    return all(results)


def run_performance_tests():
    """Exécute les tests de performance"""
    log_header("Tests de Performance")

    perf_test = Path(__file__).parent / "performance_tests.py"
    if perf_test.exists():
        success, _ = run_command(f"python {perf_test}", "Tests de performance")
        return success
    else:
        log_warn("Fichier performance_tests.py non trouvé - ignoré")
        return True


def run_coverage_analysis():
    """Exécute l'analyse de couverture de code"""
    log_header("Analyse de Couverture de Code")

    # Vérifier si coverage est installé
    success, _ = run_command(
        "python -c 'import coverage'", "Vérification de l'installation de coverage"
    )

    if not success:
        log_warn("Module coverage non installé - ignoré")
        return True

    # Exécuter les tests avec couverture
    success1, _ = run_command(
        "cd app && coverage run --source='.' manage.py test",
        "Exécution des tests avec couverture",
    )

    if success1:
        # Générer le rapport
        success2, output = run_command(
            "cd app && coverage report --show-missing",
            "Génération du rapport de couverture",
        )

        if success2:
            print(output)

        # Générer le rapport HTML
        run_command("cd app && coverage html", "Génération du rapport HTML")

    return success1


def check_code_quality():
    """Vérifie la qualité du code avec flake8 si disponible"""
    log_header("Vérification de la Qualité du Code")

    # Vérifier si flake8 est installé
    success, _ = run_command(
        "python -c 'import flake8'", "Vérification de l'installation de flake8"
    )

    if not success:
        log_warn("Module flake8 non installé - ignoré")
        return True

    # Exécuter flake8
    success, output = run_command(
        "flake8 app/ --max-line-length=120 --exclude=migrations,venv",
        "Analyse statique du code",
    )

    if success:
        log_success("Code conforme aux standards PEP8")
    else:
        log_warn("Problèmes de qualité de code détectés:")
        print(output)

    return True  # Ne pas faire échouer le test pour la qualité


def main():
    """Fonction principale"""
    log_header("🧪 Suite de Tests ICTGROUP Website")

    start_time = time.time()

    # Liste des tests à exécuter
    tests = [
        ("Vérification Django", check_django_setup),
        ("Tests Unitaires", run_unit_tests),
        ("Tests Personnalisés", run_custom_tests),
        ("Tests de Performance", run_performance_tests),
        ("Couverture de Code", run_coverage_analysis),
        ("Qualité du Code", check_code_quality),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            log_error(f"Erreur lors de {test_name}: {str(e)}")
            results.append((test_name, False))

    # Résumé des résultats
    log_header("📊 Résumé des Tests")

    passed = 0
    total = len(results)

    for test_name, result in results:
        if result:
            print(f"✅ {test_name}")
            passed += 1
        else:
            print(f"❌ {test_name}")

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n📈 Résultats: {passed}/{total} tests réussis")
    print(f"⏱️  Durée totale: {duration:.2f} secondes")

    if passed == total:
        log_success("🎉 Tous les tests sont passés avec succès!")
        return 0
    else:
        log_error(f"❌ {total - passed} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
