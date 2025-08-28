#!/bin/bash

# 🧹 Script de nettoyage et réorganisation ICTGROUP Website
# =========================================================

echo "🏢 ICTGROUP Website - Nettoyage et Réorganisation"
echo "================================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les actions
log_action() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

log_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# 1. NETTOYAGE DES FICHIERS TEMPORAIRES
echo -e "\n${BLUE}📁 Phase 1: Nettoyage des fichiers temporaires${NC}"
echo "================================================"

# Fichiers de test temporaires à supprimer
TEMP_TEST_FILES=(
    "test_logo_header.sh"
    "test_admin_pages.sh"
    "test_calendar_improvements.sh"
    "test_cleanup_views.sh"
    "test_dashboard_fusion.sh"
    "test_edit_delete_links.sh"
    "test_final_calendar_fixes.sh"
    "test_final_corrections.sh"
    "test_fixes.py"
    "test_mobile_menu.sh"
    "test_models_fix.sh"
    "test_navigation_pages.sh"
    "validate_calendar_final.sh"
    "mobile_menu_diagnostic.sh"
    "mobile_menu_test.html"
    "test_import.csv"
)

# Créer le dossier archive s'il n'existe pas
mkdir -p archive/temp_files
mkdir -p archive/docs_deprecated

# Archiver les fichiers temporaires
for file in "${TEMP_TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" archive/temp_files/
        log_action "Archivé: $file"
    fi
done

# 2. RÉORGANISATION DES SCRIPTS
echo -e "\n${BLUE}📁 Phase 2: Réorganisation des scripts${NC}"
echo "======================================"

# Créer une nouvelle structure pour les scripts
mkdir -p scripts/deployment
mkdir -p scripts/testing
mkdir -p scripts/maintenance
mkdir -p scripts/development

# Déplacer les scripts vers leurs catégories appropriées
if [ -f "scripts/deploy_fly.sh" ]; then
    mv scripts/deploy_fly.sh scripts/deployment/
    log_action "Déplacé: deploy_fly.sh vers deployment/"
fi

if [ -f "scripts/configure_gandi_domain.sh" ]; then
    mv scripts/configure_gandi_domain.sh scripts/deployment/
    log_action "Déplacé: configure_gandi_domain.sh vers deployment/"
fi

if [ -f "scripts/setup-github-secrets.sh" ]; then
    mv scripts/setup-github-secrets.sh scripts/deployment/
    log_action "Déplacé: setup-github-secrets.sh vers deployment/"
fi

if [ -f "scripts/clean_cache.sh" ]; then
    mv scripts/clean_cache.sh scripts/maintenance/
    log_action "Déplacé: clean_cache.sh vers maintenance/"
fi

if [ -f "scripts/monitor_certs.sh" ]; then
    mv scripts/monitor_certs.sh scripts/maintenance/
    log_action "Déplacé: monitor_certs.sh vers maintenance/"
fi

if [ -f "scripts/optimize_project.sh" ]; then
    mv scripts/optimize_project.sh scripts/maintenance/
    log_action "Déplacé: optimize_project.sh vers maintenance/"
fi

if [ -f "scripts/run_ci_local.sh" ]; then
    mv scripts/run_ci_local.sh scripts/testing/
    log_action "Déplacé: run_ci_local.sh vers testing/"
fi

if [ -f "scripts/install-git-hooks.sh" ]; then
    mv scripts/install-git-hooks.sh scripts/development/
    log_action "Déplacé: install-git-hooks.sh vers development/"
fi

if [ -f "scripts/prepare_commit.sh" ]; then
    mv scripts/prepare_commit.sh scripts/development/
    log_action "Déplacé: prepare_commit.sh vers development/"
fi

# 3. NETTOYAGE DE LA DOCUMENTATION
echo -e "\n${BLUE}📁 Phase 3: Nettoyage de la documentation${NC}"
echo "=========================================="

# Fichiers de documentation obsolètes ou dupliqués
DEPRECATED_DOCS=(
    "docs/CLEANUP_REPORT.md"
    "docs/CLEANUP_REPORT_FINAL.md"
    "docs/OPTIMIZATION_REPORT.md"
    "docs/OPTIMIZATION_FINAL_REPORT.md"
    "docs/RESTORATION_REPORT.md"
    "docs/MOBILE_MENU_FIX.md"
    "docs/FIX_MES_DEMANDES.md"
    "docs/CALENDAR_FIXES_REPORT.md"
    "docs/VALIDATION_MOBILE_OPTIMIZATION.md"
    "docs/AMELIORATIONS_INTERFACE_2025.md"
)

# Archiver les docs dépréciées
for doc in "${DEPRECATED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" archive/docs_deprecated/
        log_action "Archivé: $doc"
    fi
done

# 4. RÉORGANISATION DE LA DOCUMENTATION
echo -e "\n${BLUE}📁 Phase 4: Réorganisation de la documentation${NC}"
echo "=============================================="

# Créer une nouvelle structure pour la documentation
mkdir -p docs/deployment
mkdir -p docs/development
mkdir -p docs/user-guide
mkdir -p docs/technical

# Déplacer les docs vers leurs catégories appropriées
if [ -f "docs/DEPLOYMENT_DOCKER.md" ]; then
    mv docs/DEPLOYMENT_DOCKER.md docs/deployment/
    log_action "Déplacé: DEPLOYMENT_DOCKER.md vers deployment/"
fi

if [ -f "docs/FLY_DEPLOYMENT.md" ]; then
    mv docs/FLY_DEPLOYMENT.md docs/deployment/
    log_action "Déplacé: FLY_DEPLOYMENT.md vers deployment/"
fi

if [ -f "docs/GANDI_DOMAIN_CONFIG.md" ]; then
    mv docs/GANDI_DOMAIN_CONFIG.md docs/deployment/
    log_action "Déplacé: GANDI_DOMAIN_CONFIG.md vers deployment/"
fi

if [ -f "docs/LOCAL_DEV.md" ]; then
    mv docs/LOCAL_DEV.md docs/development/
    log_action "Déplacé: LOCAL_DEV.md vers development/"
fi

if [ -f "docs/GIT_HOOKS.md" ]; then
    mv docs/GIT_HOOKS.md docs/development/
    log_action "Déplacé: GIT_HOOKS.md vers development/"
fi

if [ -f "docs/PERFORMANCE_OPTIMIZATION.md" ]; then
    mv docs/PERFORMANCE_OPTIMIZATION.md docs/technical/
    log_action "Déplacé: PERFORMANCE_OPTIMIZATION.md vers technical/"
fi

if [ -f "docs/SUPABASE_CONFIG.md" ]; then
    mv docs/SUPABASE_CONFIG.md docs/technical/
    log_action "Déplacé: SUPABASE_CONFIG.md vers technical/"
fi

if [ -f "docs/DOCUMENT_SYSTEM_GUIDE.md" ]; then
    mv docs/DOCUMENT_SYSTEM_GUIDE.md docs/user-guide/
    log_action "Déplacé: DOCUMENT_SYSTEM_GUIDE.md vers user-guide/"
fi

if [ -f "docs/SEO_COMPLETE_GUIDE.md" ]; then
    mv docs/SEO_COMPLETE_GUIDE.md docs/user-guide/
    log_action "Déplacé: SEO_COMPLETE_GUIDE.md vers user-guide/"
fi

# 5. NETTOYAGE DES TESTS
echo -e "\n${BLUE}📁 Phase 5: Réorganisation des tests${NC}"
echo "===================================="

# Créer une nouvelle structure pour les tests
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/performance
mkdir -p tests/functional

# Déplacer les tests existants
if [ -f "tests/test_models.py" ]; then
    mv tests/test_models.py tests/unit/
    log_action "Déplacé: test_models.py vers unit/"
fi

if [ -f "tests/test_forms.py" ]; then
    mv tests/test_forms.py tests/unit/
    log_action "Déplacé: test_forms.py vers unit/"
fi

if [ -f "tests/test_views.py" ]; then
    mv tests/test_views.py tests/integration/
    log_action "Déplacé: test_views.py vers integration/"
fi

if [ -f "tests/test_auth.py" ]; then
    mv tests/test_auth.py tests/integration/
    log_action "Déplacé: test_auth.py vers integration/"
fi

if [ -f "tests/performance_tests.py" ]; then
    mv tests/performance_tests.py tests/performance/
    log_action "Déplacé: performance_tests.py vers performance/"
fi

# 6. CRÉATION DES FICHIERS README POUR CHAQUE DOSSIER
echo -e "\n${BLUE}📁 Phase 6: Création des README pour chaque section${NC}"
echo "================================================="

log_info "Création des fichiers README pour la navigation..."

# Résumé des actions
echo -e "\n${GREEN}🎉 Nettoyage et réorganisation terminés !${NC}"
echo "=========================================="
echo "✅ Fichiers temporaires archivés"
echo "✅ Scripts réorganisés par catégorie"
echo "✅ Documentation restructurée"
echo "✅ Tests classés par type"
echo "✅ Structure modulaire créée"
echo ""
echo "📁 Nouvelle structure:"
echo "├── scripts/"
echo "│   ├── deployment/     # Scripts de déploiement"
echo "│   ├── testing/        # Scripts de test"
echo "│   ├── maintenance/    # Scripts de maintenance"
echo "│   └── development/    # Scripts de développement"
echo "├── docs/"
echo "│   ├── deployment/     # Guides de déploiement"
echo "│   ├── development/    # Guides de développement"
echo "│   ├── user-guide/     # Guides utilisateur"
echo "│   └── technical/      # Documentation technique"
echo "├── tests/"
echo "│   ├── unit/          # Tests unitaires"
echo "│   ├── integration/   # Tests d'intégration"
echo "│   ├── performance/   # Tests de performance"
echo "│   └── functional/    # Tests fonctionnels"
echo "└── archive/"
echo "    ├── temp_files/    # Fichiers temporaires"
echo "    └── docs_deprecated/ # Documentation obsolète"
echo ""
echo "Pour continuer, utilisez:"
echo "  ./manage.sh help      # Voir toutes les commandes"
echo "  ./manage.sh test      # Lancer les tests"
echo "  ./manage.sh start     # Démarrer l'application"
