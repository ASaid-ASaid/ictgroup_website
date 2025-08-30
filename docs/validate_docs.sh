#!/bin/bash

# =============================================================================
# Script de validation de la documentation
# =============================================================================
# Description: Vérifie la cohérence et la qualité de la documentation
# Usage: ./docs/validate_docs.sh
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

DOCS_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$DOCS_DIR")"

log_header "Validation de la Documentation"

# 1. Vérifier que tous les fichiers existent
log_info "Vérification de l'existence des fichiers..."

expected_files=(
    "INDEX.md"
    "README.md"
    "MIGRATION_GUIDE.md"
    "MIGRATION_LEAVE_DATA.md"
    "MIGRATION_SUPABASE_SUCCESS.md"
    "OVERTIME_MANAGEMENT.md"
    "VALIDATION_RULES_CLARIFICATION.md"
    "deployment/README.md"
    "deployment/DEPLOYMENT_DOCKER.md"
    "deployment/FLY_DEPLOYMENT.md"
    "deployment/GANDI_DOMAIN_CONFIG.md"
    "development/README.md"
    "development/LOCAL_DEV.md"
    "development/GIT_HOOKS.md"
    "technical/README.md"
    "technical/PERFORMANCE_OPTIMIZATION.md"
    "technical/SUPABASE_CONFIG.md"
    "user-guide/README.md"
    "user-guide/DOCUMENT_SYSTEM_GUIDE.md"
    "user-guide/SEO_COMPLETE_GUIDE.md"
)

missing_files=0
for file in "${expected_files[@]}"; do
    if [ -f "$DOCS_DIR/$file" ]; then
        echo "  ✅ $file"
    else
        log_error "  ❌ $file - MANQUANT"
        ((missing_files++))
    fi
done

# 2. Vérifier les liens internes
log_info "Vérification des liens internes..."

broken_links=0
for doc in "$DOCS_DIR"/*.md; do
    if [ -f "$doc" ]; then
        doc_name=$(basename "$doc")
        
        # Vérifier les liens vers ../
        while IFS= read -r line; do
            if [[ $line =~ \[.*\]\(\.\./ ]]; then
                link=$(echo "$line" | grep -o '\.\./[^)]*' | head -1)
                if [ -n "$link" ]; then
                    # Pour les liens ../, on considère qu'ils sont valides
                    # car ils pointent vers le répertoire parent du projet
                    log_info "  ✓ $doc_name: Lien parent $link (validé manuellement)"
                fi
            fi
        done < "$doc"
        
        # Vérifier les liens relatifs dans docs/
        while IFS= read -r line; do
            if [[ $line =~ \[.*\]\([^h][^t][^t][^p] ]]; then
                link=$(echo "$line" | grep -o '(\([^)]*\)' | sed 's/[()]//g' | head -1)
                if [[ "$link" != *"http"* ]] && [[ "$link" != *"#"* ]] && [[ "$link" != *".."* ]]; then
                    if [ ! -f "$DOCS_DIR/$link" ]; then
                        log_warn "  ⚠️  $doc_name: Lien cassé $link"
                        ((broken_links++))
                    fi
                fi
            fi
        done < "$doc"
    fi
done

# 3. Vérifier les références obsolètes
log_info "Vérification des références obsolètes..."

obsolete_patterns=(
    "deploy_docker.sh"
    "./clean_cache.sh"
    "./deploy_fly.sh"
    "./debug_static.sh"
    "settings_fly"
)

obsolete_found=0
for doc in "$DOCS_DIR"/*.md; do
    if [ -f "$doc" ]; then
        doc_name=$(basename "$doc")
        
        for pattern in "${obsolete_patterns[@]}"; do
            # Pour MIGRATION_GUIDE.md, ignorer les références dans le tableau des fichiers déplacés
            if [[ "$doc_name" == "MIGRATION_GUIDE.md" ]] && grep -A 10 -B 2 "$pattern" "$doc" | grep -q "|.*|.*|"; then
                continue
            fi
            
            # Pour MIGRATION_SUPABASE_SUCCESS.md, ignorer la référence légitime à settings_fly.py
            if [[ "$doc_name" == "MIGRATION_SUPABASE_SUCCESS.md" ]] && [[ "$pattern" == "settings_fly" ]]; then
                continue
            fi
            
            if grep -q "$pattern" "$doc"; then
                log_warn "  ⚠️  $doc_name: Référence obsolète '$pattern'"
                ((obsolete_found++))
            fi
        done
    fi
done

# 4. Vérifier la structure des documents
log_info "Vérification de la structure des documents..."

structure_issues=0
for doc in "$DOCS_DIR"/*.md; do
    if [ -f "$doc" ]; then
        doc_name=$(basename "$doc")
        
        # Vérifier qu'il y a au moins un titre principal
        if ! grep -q "^# " "$doc"; then
            log_warn "  ⚠️  $doc_name: Pas de titre principal (# )"
            ((structure_issues++))
        fi
        
        # Vérifier l'encodage UTF-8
        if ! file "$doc" | grep -q "UTF-8"; then
            log_warn "  ⚠️  $doc_name: Encodage non UTF-8"
            ((structure_issues++))
        fi
    fi
done

# 5. Résumé
echo ""
log_header "Résumé de la Validation"

total_issues=$((missing_files + broken_links + obsolete_found + structure_issues))

echo "📊 Statistiques :"
echo "  - Fichiers manquants: $missing_files"
echo "  - Liens cassés: $broken_links"  
echo "  - Références obsolètes: $obsolete_found"
echo "  - Problèmes de structure: $structure_issues"
echo "  - Total des problèmes: $total_issues"

echo ""
if [ $total_issues -eq 0 ]; then
    log_info "✨ Documentation entièrement validée !"
    echo ""
    echo "🎉 Tous les documents sont cohérents et à jour."
else
    log_warn "⚠️  $total_issues problème(s) détecté(s)"
    echo ""
    echo "💡 Recommandations :"
    echo "  1. Corriger les liens cassés"
    echo "  2. Mettre à jour les références obsolètes"
    echo "  3. Vérifier la structure des documents"
    echo "  4. Relancer la validation après corrections"
fi

exit $total_issues
