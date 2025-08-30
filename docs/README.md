# 📚 Documentation ICTGROUP Website

> **Dossier de documentation technique centralisée** - Version mise à jour Août 2025

## 📋 Vue d'Ensemble

Ce dossier contient toute la documentation technique du projet ICTGROUP Website, organisée par thématiques pour faciliter la navigation et la maintenance.

## 🗂️ Structure des Documents

### 📖 **Guides Principaux**
- **[INDEX.md](INDEX.md)** - Table des matières principale
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Guide de migration vers la nouvelle structure

### 🔧 **Configuration & Déploiement**
- **[FLY_DEPLOYMENT.md](deployment/FLY_DEPLOYMENT.md)** - Déploiement sur Fly.io
- **[DEPLOYMENT_DOCKER.md](deployment/DEPLOYMENT_DOCKER.md)** - Configuration Docker
- **[SUPABASE_CONFIG.md](technical/SUPABASE_CONFIG.md)** - Configuration Supabase
- **[GANDI_DOMAIN_CONFIG.md](deployment/GANDI_DOMAIN_CONFIG.md)** - Configuration DNS

### 📊 **Rapports & Optimisation**
- **[MIGRATION_SUPABASE_SUCCESS.md](MIGRATION_SUPABASE_SUCCESS.md)** - Rapport migration Supabase
- **[PERFORMANCE_OPTIMIZATION.md](technical/PERFORMANCE_OPTIMIZATION.md)** - Guide optimisation
- **[OVERTIME_MANAGEMENT.md](OVERTIME_MANAGEMENT.md)** - Gestion des heures supplémentaires

### 👥 **Guides Utilisateur**
- **[DOCUMENT_SYSTEM_GUIDE.md](user-guide/DOCUMENT_SYSTEM_GUIDE.md)** - Guide système documentaire
- **[SEO_COMPLETE_GUIDE.md](user-guide/SEO_COMPLETE_GUIDE.md)** - Guide SEO complet

### 🧪 **Tests & Validation**
- **[VALIDATION_RULES_CLARIFICATION.md](VALIDATION_RULES_CLARIFICATION.md)** - Règles de validation

## 🎯 Navigation Rapide

### Pour les Développeurs
```bash
# Commencer ici
cat docs/INDEX.md

# Installation rapide
./manage.sh dev:start

# Documentation complète
./manage.sh docs:serve
```

### Pour les Administrateurs
```bash
# Déploiement
./manage.sh deploy:fly

# Configuration Supabase
cat docs/technical/SUPABASE_CONFIG.md

# Configuration domaine
cat docs/deployment/GANDI_DOMAIN_CONFIG.md
```

### Pour les Utilisateurs
```bash
# Guide d'utilisation
cat docs/user-guide/README.md

# Système documentaire
cat docs/user-guide/DOCUMENT_SYSTEM_GUIDE.md
```

### Pour la Maintenance
```bash
# Performance
cat docs/PERFORMANCE_OPTIMIZATION.md

# Migration/Mise à jour
cat docs/MIGRATION_GUIDE.md
```

## 📝 Standards de Documentation

### Format des Documents
- **Format** : Markdown (.md)
- **Encodage** : UTF-8
- **Emojis** : Utilisés pour la catégorisation visuelle
- **Liens** : Relatifs au projet quand possible

### Structure Type
```markdown
# 📚 Titre Principal

> **Résumé du document**

## 📋 Section 1
## 🔧 Section 2
## 🚀 Section 3

---
*Footer avec liens de navigation*
```

### Maintenance
- **Mise à jour** : Lors des changements majeurs
- **Validation** : Vérification des liens
- **Versioning** : Via Git avec le reste du projet

## 🔗 Liens Externes

- **Projet Principal** : [README.md](../README.md)
- **Scripts** : [scripts/README.md](../scripts/README.md)
- **Repository** : [GitHub - ictgroup_website](https://github.com/ASaid-ASaid/ictgroup_website)

## 🆘 Support

En cas de problème avec la documentation :

1. **Vérifier** l'[INDEX.md](INDEX.md) pour la navigation
2. **Consulter** le [guide de migration](MIGRATION_GUIDE.md) pour les changements
3. **Ouvrir une issue** sur GitHub si nécessaire

---

<div align="center">

**[🏠 Retour à l'accueil](../README.md) • [📚 Index Documentation](INDEX.md) • [🚀 Démarrage Rapide](../README.md#-démarrage-rapide)**

*Documentation maintenue et organisée - ICTGROUP Team*

</div>

1. **Cloner le dépôt**
2. **Copier le fichier `.env.example` en `.env` et adapter les variables**
3. **Construire et lancer avec Docker**
   ```sh
   docker-compose up --build
   ```
4. **Accéder à l'application**
   - Vitrine : http://localhost:8000/
   - Extranet : http://localhost:8000/extranet/

---

## Variables d'environnement
Voir `.env.example` pour la configuration.

---

## Collecte des fichiers statiques
En production, les fichiers statiques sont collectés automatiquement dans l'image Docker.

---

## Bonnes pratiques
- Ne jamais commiter de vraies clés secrètes ou mots de passe.
- Ajouter des tests unitaires dans `tests/`.
- Utiliser un reverse proxy (Nginx) en production.
- Ajouter les dossiers `__pycache__/`, `*.pyc`, `logs/`, `.env` au `.gitignore`.

---

## Accès à l'interface graphique PostgreSQL (Adminer)

Pour gérer la base de données PostgreSQL via une interface web :

1. **Lancer les services Docker** (si ce n'est pas déjà fait) :
   ```sh
   docker-compose up --build
   ```
2. **Ouvrir Adminer dans votre navigateur** : [http://localhost:8080](http://localhost:8080)
3. **Renseigner les informations de connexion** :
   - **SGBD** : PostgreSQL
   - **Serveur** : db
   - **Utilisateur** : (valeur de `DB_USER` dans `.env`)
   - **Mot de passe** : (valeur de `DB_PASSWORD` dans `.env`)
   - **Base** : (valeur de `DB_NAME` dans `.env`)


/sh source venv/bin/activate

Vous pouvez ainsi visualiser, éditer et administrer vos tables PostgreSQL facilement.

---

## Auteur
ahmed.said@ictgroup.fr
