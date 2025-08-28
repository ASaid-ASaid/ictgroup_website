# 🔧 Scripts de Maintenance

Scripts pour la maintenance système et l'optimisation du projet.

## 📁 Contenu

### 🧹 clean_cache.sh
Nettoyage du cache système
- Cache Django
- Cache Supabase
- Fichiers temporaires
- Logs anciens

### 📊 monitor_certs.sh
Surveillance des certificats SSL
- Vérification expiration
- Renouvellement automatique
- Alertes email

### ⚡ optimize_project.sh
Optimisation globale du projet
- Compression fichiers statiques
- Optimisation base de données
- Nettoyage Docker
- Analyse performance

## 🔧 Utilisation

```bash
# Nettoyage complet
./manage.sh clean

# Cache uniquement
./scripts/maintenance/clean_cache.sh

# Surveillance certificats
./scripts/maintenance/monitor_certs.sh

# Optimisation projet
./scripts/maintenance/optimize_project.sh
```

## ⏰ Tâches Automatisées

### Cron Jobs Recommandés

```bash
# Nettoyage quotidien (3h du matin)
0 3 * * * /path/to/scripts/maintenance/clean_cache.sh

# Vérification certificats (hebdomadaire)
0 6 * * 1 /path/to/scripts/maintenance/monitor_certs.sh

# Optimisation mensuelle
0 2 1 * * /path/to/scripts/maintenance/optimize_project.sh
```

## 📊 Monitoring

Les scripts génèrent des logs dans:
- `logs/maintenance.log` - Actions maintenance
- `logs/certificates.log` - État certificats
- `logs/optimization.log` - Optimisations effectuées

## ⚠️ Précautions

- Sauvegarder avant optimisation
- Tester en développement
- Surveiller l'usage ressources
- Vérifier les performances post-maintenance
