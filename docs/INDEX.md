# 📚 Documentation ICTGROUP Website

> **Centre de documentation technique et guides d'utilisation**

## 📋 Table des Matières

### 🚀 Getting Started
- [**README Principal**](../README.md) - Guide complet du projet
- [**Installation Rapide**](../README.md#️-installation) - Démarrage en 5 minutes
- [**Guide de Migration**](MIGRATION_GUIDE.md) - ⭐ **NOUVEAU** - Transition vers la nouvelle structure

### 🔧 Configuration et Déploiement
- [**Configuration Supabase**](SUPABASE_CONFIG.md) - Guide complet Supabase
- [**Déploiement Fly.io**](FLY_DEPLOYMENT.md) - Production sur Fly.io
- [**Configuration Docker**](DEPLOYMENT_DOCKER.md) - Environnement Docker
- [**Configuration Domaine Gandi**](GANDI_DOMAIN_CONFIG.md) - DNS et domaine

### 📊 Base de Données et Migration
- [**Migration Supabase Réussie**](MIGRATION_SUPABASE_SUCCESS.md) - Rapport de migration
- [**Script SQL Supabase**](../config/supabase_setup.sql) - Tables analytics

### 📋 Rapports et Maintenance
- [**Rapport de Nettoyage Documentation**](CLEANUP_REPORT.md) - ⭐ **NOUVEAU** - Audit et optimisation docs

### ⚡ Performance et Optimisation
- [**Optimisations Performance**](PERFORMANCE_OPTIMIZATION.md) - Guide d'optimisation
- [**Tests Performance**](../tests/performance_tests.py) - Scripts de test

### 🛠️ Scripts et Outils
- [**Script Principal**](../manage.sh) - Gestion centralisée
- [**Scripts de Déploiement**](../scripts/) - Automatisation

## 🏗️ Architecture du Projet

```
ictgroup_website/
├── 📱 app/                     # Application Django
│   ├── extranet/              # Module extranet employés
│   ├── vitrine/               # Module site vitrine
│   └── ictgroup/              # Configuration Django
├── 🔧 scripts/                # Scripts d'automatisation
│   ├── clean_cache.sh         # Nettoyage cache
│   ├── debug_static.sh        # Debug fichiers statiques
│   ├── deploy_fly.sh          # Déploiement Fly.io
│   └── maintain_scripts.sh    # Maintenance scripts
├── 🧪 tests/                  # Tests automatisés
│   └── performance_tests.py   # Tests de performance
├── 📚 docs/                   # Documentation (ce dossier)
├── 🐳 docker/                 # Configuration Docker
│   ├── Dockerfile             # Image Docker principale
│   └── docker-compose-old.yml # Ancienne config
├── ⚙️ config/                 # Fichiers de configuration
│   ├── fly.toml               # Configuration Fly.io
│   ├── Procfile               # Configuration Heroku/Fly
│   ├── runtime.txt            # Version Python
│   └── supabase_setup.sql     # Tables Supabase
└── 🛠️ manage.sh               # Script principal de gestion
```

---

<div align="center">

**[🏠 Retour au README](../README.md) • [🚀 Démarrage Rapide](../README.md#-démarrage-rapide) • [📞 Support](../README.md#-support)**

*Documentation maintenue par l'équipe ICTGROUP*

</div>
