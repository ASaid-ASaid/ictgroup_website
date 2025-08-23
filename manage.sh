#!/bin/bash

# =============================================================================
# ICTGROUP Website - Script Principal de Gestion
# =============================================================================
# Description: Script principal pour gérer le projet ICTGROUP Website
# Usage: ./manage.sh [command] [options]
# Auteur: ICTGROUP Development Team
# Version: 2.0
# =============================================================================

set -e

# Configuration des couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration des chemins
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
DOCKER_DIR="$PROJECT_ROOT/docker"
CONFIG_DIR="$PROJECT_ROOT/config"
TESTS_DIR="$PROJECT_ROOT/tests"

# Fonctions utilitaires
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_header() {
    echo -e "${CYAN}=== $1 ===${NC}"
}

# Fonction d'aide
show_help() {
    cat << EOF
${CYAN}ICTGROUP Website - Script de Gestion${NC}

${YELLOW}USAGE:${NC}
    ./manage.sh [COMMAND] [OPTIONS]

${YELLOW}COMMANDES DISPONIBLES:${NC}

${GREEN}Développement:${NC}
    dev:start           Démarrer l'environnement de développement
    dev:stop            Arrêter l'environnement de développement
    dev:restart         Redémarrer l'environnement de développement
    dev:logs            Voir les logs en temps réel
    dev:shell           Ouvrir un shell dans le container
    dev:migrate         Exécuter les migrations Django
    dev:superuser       Créer un superutilisateur

${GREEN}Nettoyage:${NC}
    clean:cache         Nettoyer le cache Python et Django
    clean:docker        Nettoyer les containers et images Docker
    clean:all           Nettoyage complet (cache + docker)

${GREEN}Tests:${NC}
    test:unit           Exécuter les tests unitaires Django
    test:performance    Exécuter les tests de performance
    test:all            Exécuter tous les tests

${GREEN}Déploiement:${NC}
    deploy:fly          Déployer sur Fly.io
    deploy:check        Vérifier la configuration de déploiement

${GREEN}Outils:${NC}
    debug:static        Diagnostiquer les fichiers statiques
    health:check        Vérifier l'état du système
    maintain:scripts    Maintenance et nettoyage des scripts

${GREEN}Sauvegarde:${NC}
    backup:db           Sauvegarder la base de données
    backup:files        Sauvegarder les fichiers média
    migrate:supabase    Migrer les données vers Supabase

${GREEN}Surveillance:${NC}
    monitor:logs        Surveiller les logs en temps réel
    monitor:resources   Surveiller les ressources système

${GREEN}Sécurité & Documentation:${NC}
    security:scan       Analyser la sécurité du code
    docs:serve          Servir la documentation
    docs:validate       Valider la cohérence des docs

${YELLOW}EXEMPLES:${NC}
    ./manage.sh dev:start           # Démarrer le développement
    ./manage.sh deploy:fly          # Déployer en production
    ./manage.sh test:all            # Exécuter tous les tests
    ./manage.sh clean:all           # Nettoyage complet

${YELLOW}RACCOURCIS:${NC}
    ./manage.sh start              # Équivalent à dev:start
    ./manage.sh stop               # Équivalent à dev:stop
    ./manage.sh deploy             # Équivalent à deploy:fly
    ./manage.sh test               # Équivalent à test:all

EOF
}

# Commandes de développement
dev_start() {
    log_header "Démarrage de l'environnement de développement"
    
    # Vérifier que Docker est démarré
    if ! docker info &> /dev/null; then
        log_error "Docker n'est pas démarré. Veuillez démarrer Docker."
        exit 1
    fi
    
    log_info "Construction et démarrage des containers..."
    docker-compose up --build -d
    
    log_info "Attente du démarrage des services..."
    sleep 5
    
    log_success "Environnement de développement démarré !"
    log_info "Application disponible sur: http://localhost:8000"
    log_info "Utilisez './manage.sh dev:logs' pour voir les logs"
}

dev_stop() {
    log_header "Arrêt de l'environnement de développement"
    docker-compose down
    log_success "Environnement arrêté"
}

dev_restart() {
    log_header "Redémarrage de l'environnement de développement"
    dev_stop
    dev_start
}

dev_logs() {
    log_header "Logs de l'application"
    docker-compose logs -f web
}

dev_shell() {
    log_header "Shell du container"
    docker-compose exec web bash
}

dev_migrate() {
    log_header "Exécution des migrations Django"
    docker-compose exec web python manage.py migrate
}

dev_superuser() {
    log_header "Création d'un superutilisateur"
    docker-compose exec web python manage.py createsuperuser
}

# Commandes de nettoyage
clean_cache() {
    log_header "Nettoyage du cache"
    if [ -f "$SCRIPTS_DIR/clean_cache.sh" ]; then
        bash "$SCRIPTS_DIR/clean_cache.sh"
    else
        log_warn "Script de nettoyage non trouvé, nettoyage manuel..."
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        log_success "Cache nettoyé"
    fi
}

clean_docker() {
    log_header "Nettoyage Docker"
    log_info "Suppression des containers arrêtés..."
    docker container prune -f
    log_info "Suppression des images non utilisées..."
    docker image prune -f
    log_info "Suppression des volumes non utilisés..."
    docker volume prune -f
    log_success "Nettoyage Docker terminé"
}

clean_all() {
    log_header "Nettoyage complet"
    clean_cache
    clean_docker
    log_success "Nettoyage complet terminé"
}

# Commandes de tests
test_unit() {
    log_header "Tests unitaires Django"
    docker-compose exec web python manage.py test
}

test_performance() {
    log_header "Tests de performance"
    if [ -f "$TESTS_DIR/performance_tests.py" ]; then
        python "$TESTS_DIR/performance_tests.py"
    else
        log_warn "Tests de performance non trouvés"
    fi
}

test_all() {
    log_header "Exécution de tous les tests"
    
    # Utiliser le script de tests complet
    if [ -f "$TESTS_DIR/run_all_tests.py" ]; then
        python "$TESTS_DIR/run_all_tests.py"
    else
        log_warn "Script de tests complet non trouvé, exécution des tests basiques..."
        test_unit
        test_performance
    fi
}

test_unit() {
    log_header "Tests unitaires Django"
    cd "$PROJECT_ROOT/app"
    python3 manage.py test extranet --verbosity=2
    cd "$PROJECT_ROOT"
}

test_coverage() {
    log_header "Tests avec couverture de code"
    cd "$PROJECT_ROOT/app"
    
    # Vérifier si coverage est installé
    if python -c "import coverage" 2>/dev/null; then
        coverage run --source='.' manage.py test extranet
        coverage report --show-missing
        coverage html
        log_success "Rapport de couverture généré dans htmlcov/"
    else
        log_warn "Module coverage non installé. Installation..."
        pip install coverage
        coverage run --source='.' manage.py test extranet
        coverage report --show-missing
    fi
    
    cd "$PROJECT_ROOT"
}

# Commandes de déploiement
deploy_fly() {
    log_header "Déploiement sur Fly.io"
    if [ -f "$SCRIPTS_DIR/deploy_fly.sh" ]; then
        bash "$SCRIPTS_DIR/deploy_fly.sh"
    else
        log_error "Script de déploiement Fly.io non trouvé"
        exit 1
    fi
}

deploy_check() {
    log_header "Vérification de la configuration de déploiement"
    log_info "Vérification des fichiers de configuration..."
    
    files_to_check=("$CONFIG_DIR/fly.toml" "$CONFIG_DIR/Procfile" "requirements.txt" ".env.example")
    
    for file in "${files_to_check[@]}"; do
        if [ -f "$file" ]; then
            log_success "✓ $file"
        else
            log_error "✗ $file manquant"
        fi
    done
}

# Outils
debug_static() {
    log_header "Diagnostic des fichiers statiques"
    if [ -f "$SCRIPTS_DIR/debug_static.sh" ]; then
        bash "$SCRIPTS_DIR/debug_static.sh"
    else
        log_warn "Script de diagnostic non trouvé"
    fi
}

maintain_scripts() {
    log_header "Maintenance des scripts"
    
    if [ -f "$SCRIPTS_DIR/maintain_scripts.sh" ]; then
        bash "$SCRIPTS_DIR/maintain_scripts.sh"
    else
        log_warn "⚠️ Script de maintenance non trouvé"
    fi
}

docs_validate() {
    log_header "Validation de la documentation"
    
    if [ -f "docs/validate_docs.sh" ]; then
        bash docs/validate_docs.sh
    else
        log_warn "⚠️ Script de validation non trouvé"
    fi
}

migrate_supabase() {
    log_header "Migration des données vers Supabase"
    
    if [ -f "$SCRIPTS_DIR/migrate_to_supabase.sh" ]; then
        bash "$SCRIPTS_DIR/migrate_to_supabase.sh"
    else
        log_error "❌ Script de migration non trouvé"
        exit 1
    fi
}

# Nouvelles fonctions avancées
backup_db() {
    log_header "Sauvegarde de la base de données"
    
    # Créer le dossier backups s'il n'existe pas
    mkdir -p backups
    
    local backup_file="backups/db_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose ps | grep -q "ictgroup-db"; then
        docker exec ictgroup-db pg_dump -U ictgroup -d ictgroup_db > "$backup_file"
        log_success "✓ Sauvegarde créée: $backup_file"
    else
        log_error "❌ Base de données non accessible"
        exit 1
    fi
}

backup_files() {
    log_header "Sauvegarde des fichiers média"
    
    mkdir -p backups
    
    local backup_file="backups/media_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    if [ -d "app/media" ]; then
        tar -czf "$backup_file" app/media/
        log_success "✓ Sauvegarde média créée: $backup_file"
    else
        log_warn "⚠️ Dossier media non trouvé"
    fi
}

monitor_logs() {
    log_header "Surveillance des logs en temps réel"
    docker-compose logs -f
}

monitor_resources() {
    log_header "Surveillance des ressources système"
    echo -e "${BLUE}📈 Utilisation des ressources Docker:${NC}"
    docker stats
}

security_scan() {
    log_header "Analyse de sécurité"
    
    if command -v bandit &> /dev/null; then
        bandit -r app/ -f json -o security_report.json
        log_success "✓ Rapport de sécurité généré: security_report.json"
    else
        log_warn "⚠️ Bandit non installé"
        echo -e "${YELLOW}Installation: pip install bandit${NC}"
    fi
}

docs_serve() {
    log_header "Serveur de documentation"
    
    if command -v mkdocs &> /dev/null; then
        mkdocs serve
    else
        log_info "📄 Ouverture de la documentation..."
        if command -v xdg-open &> /dev/null; then
            xdg-open docs/INDEX.md
        elif command -v open &> /dev/null; then
            open docs/INDEX.md
        else
            echo -e "${YELLOW}Voir: docs/INDEX.md${NC}"
        fi
    fi
}

health_check() {
    log_header "Vérification de l'état du système"
    
    # Vérifier Docker
    if docker info &> /dev/null; then
        log_success "✓ Docker est démarré"
    else
        log_error "✗ Docker n'est pas démarré"
    fi
    
    # Vérifier les containers
    if docker-compose ps | grep -q "Up"; then
        log_success "✓ Containers en cours d'exécution"
    else
        log_warn "! Aucun container en cours d'exécution"
    fi
    
    # Vérifier l'application web
    if curl -s http://localhost:8000 &> /dev/null; then
        log_success "✓ Application web accessible"
    else
        log_warn "! Application web non accessible"
    fi
}

# Fonction principale
main() {
    case "${1:-help}" in
        # Commandes de développement
        "dev:start"|"start")
            dev_start
            ;;
        "dev:stop"|"stop")
            dev_stop
            ;;
        "dev:restart"|"restart")
            dev_restart
            ;;
        "dev:logs"|"logs")
            dev_logs
            ;;
        "dev:shell"|"shell")
            dev_shell
            ;;
        "dev:migrate"|"migrate")
            dev_migrate
            ;;
        "dev:superuser"|"superuser")
            dev_superuser
            ;;
        
        # Commandes de nettoyage
        "clean:cache")
            clean_cache
            ;;
        "clean:docker")
            clean_docker
            ;;
        "clean:all"|"clean")
            clean_all
            ;;
        
        # Commandes de tests
        "test:unit")
            test_unit
            ;;
        "test:coverage")
            test_coverage
            ;;
        "test:performance")
            test_performance
            ;;
        "test:all"|"test")
            test_all
            ;;
        
        # Commandes de déploiement
        "deploy:fly"|"deploy")
            deploy_fly
            ;;
        "deploy:check")
            deploy_check
            ;;
        
        # Outils
        "debug:static")
            debug_static
            ;;
        "health:check"|"health")
            health_check
            ;;
        "maintain:scripts")
            maintain_scripts
            ;;
        
        # Nouvelles commandes avancées
        "backup:db")
            backup_db
            ;;
        "backup:files")
            backup_files
            ;;
        "monitor:logs")
            monitor_logs
            ;;
        "monitor:resources")
            monitor_resources
            ;;
        "security:scan")
            security_scan
            ;;
        "docs:serve")
            docs_serve
            ;;
        "docs:validate")
            docs_validate
            ;;
        
        # Aide
        "help"|"--help"|"-h")
            show_help
            ;;
        
        *)
            log_error "Commande inconnue: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Point d'entrée
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
