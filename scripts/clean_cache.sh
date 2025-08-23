#!/bin/bash

# =============================================================================
# Script de nettoyage automatique des fichiers cache et temporaires
# =============================================================================
# Description: Nettoie les caches Python, Django et Docker
# Usage: ./scripts/clean_cache.sh
# Auteur: ICTGROUP Development Team
# =============================================================================

set -e

# Configuration des couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "🧹 Nettoyage des fichiers cache et temporaires..."
echo "================================================"

# Nettoyage du cache Python dans le container
log_info "Nettoyage du cache Python dans le container..."
docker-compose exec web find /code -name "*.pyc" -delete 2>/dev/null || true
docker-compose exec web find /code -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Nettoyage local (hôte) des fichiers cache
log_info "Nettoyage du cache Python local..."
find app/ -name "*.pyc" -delete 2>/dev/null || true
find app/ -name "*.pyo" -delete 2>/dev/null || true
find app/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Nettoyage des logs
log_info "Nettoyage des fichiers de logs..."
find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true

# Nettoyage Django dans le container
log_info "Nettoyage du cache Django..."
docker-compose exec web python manage.py clearsessions 2>/dev/null || log_warn "Impossible de nettoyer les sessions Django"
find app/*/migrations/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find app/*/migrations/ -name "*.pyc" -delete 2>/dev/null || true

# Nettoyage des templatetags
echo "Nettoyage du cache des templatetags..."
find app/*/templatetags/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find app/*/templatetags/ -name "*.pyc" -delete 2>/dev/null || true

# Supprimer les logs anciens (optionnel)
echo "Nettoyage des logs anciens..."
find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true

# Nettoyage des fichiers temporaires Django
echo "Nettoyage des fichiers temporaires Django..."
find app/ -name "*.log" -delete 2>/dev/null || true
find app/ -name "*.sqlite3" -delete 2>/dev/null || true

# Vérification des migrations dupliquées
echo "Vérification des migrations dupliquées..."
duplicate_migrations=$(find app/*/migrations/ -name "*.py" ! -name "__init__.py" | xargs basename -a | sort | uniq -d)
if [ ! -z "$duplicate_migrations" ]; then
    echo "⚠️  Migrations potentiellement dupliquées détectées:"
    echo "$duplicate_migrations"
    echo "Vérifiez manuellement les fichiers de migration."
else
    echo "✅ Aucune migration dupliquée détectée."
fi

echo "✅ Nettoyage terminé!"
