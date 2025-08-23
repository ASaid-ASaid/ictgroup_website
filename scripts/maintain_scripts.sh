#!/bin/bash

# =============================================================================
# Script de maintenance et nettoyage du dossier scripts
# =============================================================================
# Description: Vérifie et nettoie les scripts obsolètes ou inutilisés
# Usage: ./scripts/maintain_scripts.sh
# Auteur: ICTGROUP Development Team
# =============================================================================

set -e

# Configuration des couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

SCRIPTS_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"

log_header "Maintenance du dossier scripts"

# Liste des scripts attendus et leur statut
declare -A EXPECTED_SCRIPTS=(
    ["clean_cache.sh"]="✅ Utilisé par manage.sh clean:cache"
    ["debug_static.sh"]="✅ Utilisé par manage.sh debug:static" 
    ["deploy_fly.sh"]="✅ Utilisé par manage.sh deploy:fly"
    ["maintain_scripts.sh"]="✅ Script de maintenance"
)

echo ""
log_info "Vérification des scripts..."

# Vérifier chaque script dans le dossier
for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ]; then
        script_name=$(basename "$script")
        
        if [[ -n "${EXPECTED_SCRIPTS[$script_name]}" ]]; then
            echo "  ✅ $script_name - ${EXPECTED_SCRIPTS[$script_name]}"
        else
            log_warn "Script non référencé: $script_name"
            
            # Vérifier s'il est utilisé dans manage.sh
            if grep -q "$script_name" "$PROJECT_ROOT/manage.sh"; then
                echo "     └── Trouvé dans manage.sh ✅"
            else
                log_error "     └── Non utilisé dans manage.sh ❌"
                echo "     └── Candidat à la suppression"
            fi
        fi
    fi
done

echo ""
log_info "Vérification des permissions..."

# Vérifier les permissions d'exécution
for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo "  ✅ $(basename "$script") - Exécutable"
        else
            log_warn "$(basename "$script") - Pas exécutable"
            chmod +x "$script"
            echo "     └── Permission corrigée ✅"
        fi
    fi
done

echo ""
log_info "Vérification de la syntaxe..."

# Vérifier la syntaxe bash de chaque script
for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ]; then
        script_name=$(basename "$script")
        if bash -n "$script" 2>/dev/null; then
            echo "  ✅ $script_name - Syntaxe correcte"
        else
            log_error "$script_name - Erreur de syntaxe"
        fi
    fi
done

echo ""
log_header "Résumé"
echo "Scripts maintenus et vérifiés :"
echo "  • clean_cache.sh - Nettoyage des caches"
echo "  • debug_static.sh - Diagnostic fichiers statiques"  
echo "  • deploy_fly.sh - Déploiement Fly.io"
echo "  • maintain_scripts.sh - Maintenance (ce script)"

echo ""
log_info "✨ Maintenance terminée !"
echo ""
echo "💡 Pour utiliser ces scripts :"
echo "   ./manage.sh clean:cache    # Utilise clean_cache.sh"
echo "   ./manage.sh debug:static   # Utilise debug_static.sh"
echo "   ./manage.sh deploy:fly     # Utilise deploy_fly.sh"
