#!/bin/bash
echo "🔧 Gestion de l'accrual automatique de congés"
echo "============================================"

cd /home/ahmed/projets/ictgroup_website

MODE=${1:-"status"}

case $MODE in
    "disable")
        echo "🚫 Désactivation de l'accrual automatique..."
        
        # Marquer l'accrual comme déjà fait pour ce mois
        docker-compose exec web python manage.py shell -c "
from django.core.cache import cache
from datetime import date
today = date.today()
cache_key = f'monthly_accrual_{today.year}_{today.month:02d}'
cache.set(cache_key, True, timeout=30*24*3600)
print(f'✅ Accrual désactivé pour {today.month}/{today.year}')
print(f'🔑 Clé cache: {cache_key}')
"
        echo "✅ Accrual automatique désactivé pour ce mois"
        ;;
        
    "enable")
        echo "✅ Réactivation de l'accrual automatique..."
        
        # Supprimer la marque d'accrual pour ce mois
        docker-compose exec web python manage.py shell -c "
from django.core.cache import cache
from datetime import date
today = date.today()
cache_key = f'monthly_accrual_{today.year}_{today.month:02d}'
cache.delete(cache_key)
print(f'✅ Accrual réactivé pour {today.month}/{today.year}')
print(f'🔑 Clé cache supprimée: {cache_key}')
"
        echo "✅ Accrual automatique réactivé"
        ;;
        
    "status")
        echo "📊 Statut de l'accrual automatique..."
        
        docker-compose exec web python manage.py shell -c "
from django.core.cache import cache
from datetime import date
today = date.today()
cache_key = f'monthly_accrual_{today.year}_{today.month:02d}'
is_disabled = cache.get(cache_key)

print(f'📅 Période actuelle: {today.month}/{today.year}')
print(f'🔑 Clé cache: {cache_key}')

if is_disabled:
    print('🚫 STATUT: DÉSACTIVÉ (accrual déjà fait ce mois)')
    print('💡 Pour réactiver: ./manage_accrual.sh enable')
else:
    print('✅ STATUT: ACTIVÉ (accrual se lancera à la prochaine connexion)')
    print('💡 Pour désactiver: ./manage_accrual.sh disable')
"
        ;;
        
    "clear-all")
        echo "🧹 Suppression de tous les caches d'accrual..."
        
        docker-compose exec web python manage.py shell -c "
from django.core.cache import cache
import re

# Récupérer toutes les clés du cache
keys = []
if hasattr(cache, '_cache'):
    keys = [key for key in cache._cache.keys() if key.startswith('monthly_accrual_')]
else:
    # Essayer les clés probables pour cette année et l'année dernière
    from datetime import date
    today = date.today()
    for year in [today.year - 1, today.year, today.year + 1]:
        for month in range(1, 13):
            key = f'monthly_accrual_{year}_{month:02d}'
            if cache.get(key):
                keys.append(key)

deleted_count = 0
for key in keys:
    cache.delete(key)
    deleted_count += 1
    print(f'🗑️  Supprimé: {key}')

print(f'✅ {deleted_count} clés d\'accrual supprimées')
print('📝 L\'accrual se relancera à la prochaine connexion pour chaque mois')
"
        ;;
        
    *)
        echo "Usage: $0 [disable|enable|status|clear-all]"
        echo ""
        echo "Commandes disponibles:"
        echo "  status     - Affiche le statut actuel de l'accrual"
        echo "  disable    - Désactive l'accrual pour ce mois"
        echo "  enable     - Réactive l'accrual pour ce mois"
        echo "  clear-all  - Supprime tous les caches d'accrual"
        echo ""
        echo "💡 En développement sur base prod, utilisez 'disable' pour éviter"
        echo "   les ajouts automatiques de jours de congés lors des connexions."
        exit 1
        ;;
esac

echo ""
echo "✅ Opération terminée !"
