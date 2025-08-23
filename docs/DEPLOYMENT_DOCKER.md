# Guide de déploiement Docker - ICTGroup Website

## État actuel du projet

✅ **Modules opérationnels :**
- `app/extranet/forms.py` - Formulaires avec validation avancée
- `app/extranet/views/` - Architecture modulaire des vues (7 modules)
- `app/extranet/models.py` - Modèles avec champ carry_over
- `app/extranet/urls.py` - URLs complètement fonctionnelles
- `scripts/clean_cache.sh` - Script de nettoyage automatique

❌ **Fichiers supprimés :**
- `models_optimized.py` - Supprimé (doublon)
- `views_old.py` - Supprimé après migration
- `migration_guide.py` - Supprimé (temporaire)
- Fichiers cache et temporaires nettoyés

## Déploiement avec Docker

### 1. Construire et démarrer l'environnement

```bash
# Via le script central (recommandé)
./manage.sh start

# Ou directement avec Docker
docker-compose build
docker-compose up -d
```

### 2. Migrations et vérifications

```bash
# Vérifier l'état des migrations
docker-compose exec web python manage.py showmigrations extranet

# Appliquer les migrations si nécessaire
docker-compose exec web python manage.py migrate extranet

# Vérifier la configuration
docker-compose exec web python manage.py check

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Nettoyage et maintenance

```bash
# Via le script central (recommandé)
./manage.sh clean:cache

# Ou directement :
./scripts/clean_cache.sh

# Ou manuellement :
docker-compose exec web find /app -name "*.pyc" -delete
docker-compose exec web find /app -name "__pycache__" -type d -exec rm -rf {} +
```

### 4. Tests des fonctionnalités

```bash
# Test des vues modulaires
docker-compose exec web python manage.py shell
```

Dans le shell Django :
```python
# Tester l'importation des nouvelles vues
from extranet.views import *

# Tester les modèles actuels
from extranet.models import LeaveRequest, TeleworkRequest, UserProfile

# Vérifier le champ carry_over
print("Champ carry_over disponible:", hasattr(UserProfile, 'carry_over'))

# Compter les objets
print(f"Utilisateurs: {UserProfile.objects.count()}")
print(f"Demandes de congés: {LeaveRequest.objects.count()}")
```

### 5. Redémarrage des services

```bash
# Redémarrer le conteneur web pour charger les nouveaux modules
docker-compose restart web

# Vérifier les logs
docker-compose logs -f web
```

### 6. Tests d'intégration

```bash
# Tester les pages principales
curl -I http://localhost:8000/extranet/
curl -I http://localhost:8000/extranet/utilisateurs/
curl -I http://localhost:8000/extranet/demandes/
curl -I http://localhost:8000/extranet/calendrier/
curl -I http://localhost:8000/extranet/magasin/stock/

# Tester les URL d'administration
curl -I http://localhost:8000/extranet/admin/conges/
curl -I http://localhost:8000/extranet/admin/teletravail/
curl -I http://localhost:8000/extranet/admin/recapitulatif/

# Exécuter les tests de performance (si disponibles)
python performance_tests.py
```

## Surveillance et débuggage

### Logs en temps réel
```bash
# Logs du conteneur web
docker-compose logs -f web

# Logs de la base de données
docker-compose logs -f db
```

### Accès aux fichiers
```bash
# Copier des fichiers depuis le conteneur
docker-compose cp web:/app/django.log ./logs/

# Accéder aux fichiers depuis l'hôte
ls -la app/extranet/views/
```

### Debug des erreurs
```bash
# Shell Django pour débugger
docker-compose exec web python manage.py shell

# Vérifier les configurations
docker-compose exec web python manage.py check

# Tester les URLs
docker-compose exec web python manage.py show_urls
```

## Structure finale actuelle

```
app/extranet/
├── forms.py                 # ✅ Formulaires avec validation
├── models.py               # ✅ Modèles avec carry_over
├── urls.py                 # ✅ URLs complètes et fonctionnelles
├── migrations/             # ✅ Migrations cohérentes (0001-0009)
│   ├── 0001_initial.py
│   ├── 0002_teleworkrequest.py
│   ├── 0003_alter_teleworkrequest_options_and_more.py
│   ├── 0004_leaverequest_admin_validated_and_more.py
│   ├── 0005_alter_userprofile_role.py
│   ├── 0006_leaverequest_demi_jour.py
│   ├── 0007_userprofile_site.py
│   ├── 0008_stockitem_stockmovement.py
│   └── 0009_userprofile_carry_over.py
├── static/                 # ✅ Fichiers statiques
├── templates/              # ✅ Templates Django
├── templatetags/           # ✅ Filtres personnalisés
└── views/                  # ✅ Architecture modulaire
    ├── __init__.py         # ✅ Exports modulaires
    ├── auth_views.py       # ✅ Authentification
    ├── dashboard_views.py  # ✅ Tableau de bord
    ├── leave_views.py      # ✅ Gestion congés
    ├── telework_views.py   # ✅ Gestion télétravail
    ├── admin_views.py      # ✅ Administration
    ├── stock_views.py      # ✅ Gestion stock
    └── calendar_views.py   # ✅ Calendrier présence
```

## Résolution de problèmes courants

### Migration carry_over résolue
- ✅ Migration 0009 corrigée et appliquée
- ✅ Colonne carry_over créée en base
- ✅ Problème NoReverseMatch résolu
- ✅ Architecture modulaire fonctionnelle

## Améliorations apportées

### 🚀 Performance
- Managers personnalisés avec `select_related()` et `prefetch_related()`
- Index de base de données sur les champs fréquemment utilisés
- Requêtes optimisées dans toutes les vues

### 🏗️ Architecture
- Séparation des préoccupations (views modulaires)
- Modèles abstraits pour éviter la duplication
- Validation automatique des données

### 🔧 Maintenabilité
- Code organisé par fonctionnalité
- Logging structuré dans tous les modules
- Documentation et commentaires détaillés

### 🛡️ Sécurité
- Validation des permissions dans chaque vue
- Protection CSRF activée
- Validation des données d'entrée renforcée

## Prochaines étapes

1. **Tester** toutes les fonctionnalités dans l'environnement Docker
2. **Valider** les performances avec les nouveaux managers
3. **Documenter** les nouvelles API et endpoints
4. **Former** l'équipe sur la nouvelle architecture

## Commandes utiles Docker

```bash
# Reconstruire complètement
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Backup de la base de données
docker-compose exec db pg_dump -U ictgroup_user -d ictgroup_db > backup.sql

# Restaurer la base de données
docker-compose exec -T db psql -U ictgroup_user -d ictgroup_db < backup.sql

# Nettoyer les images inutilisées
docker system prune -f

# Nettoyage automatique du cache
./manage.sh clean:cache

# Vérifier les logs en continu
docker-compose logs -f web
```

## Tests de performance

Pour exécuter les tests de performance :

```bash
# Exécuter le module de tests de performance
python performance_tests.py

# Ou dans le container Docker
docker-compose exec web python /app/performance_tests.py
```

Note: Le fichier `performance_tests.py` n'est pas versionné dans Git pour éviter l'encombrement du repository.
