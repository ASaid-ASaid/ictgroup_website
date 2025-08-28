# 📚 Documentation ICTGROUP Website

> **Index principal de la documentation** - Navigation organisée par expertise

## 🎯 Navigation Rapide

### 🆕 Nouveau sur le projet ?
Commencez par les guides de démarrage appropriés à votre rôle :

| Rôle | Guide de Démarrage | Description |
|------|-------------------|-------------|
| **👨‍💻 Développeur** | [`development/README.md`](development/) | Setup environnement, outils, workflow |
| **🚀 DevOps** | [`deployment/README.md`](deployment/) | Déploiement, infrastructure, monitoring |
| **👤 Utilisateur** | [`user-guide/README.md`](user-guide/) | Guide d'utilisation de la plateforme |
| **🔧 Admin Système** | [`technical/README.md`](technical/) | Architecture, APIs, optimisation |

## 📁 Structure Documentation

### 🚀 Déploiement (`deployment/`)
Documentation pour mettre l'application en production.

**Contenu :**
- **[README.md](deployment/README.md)** - Vue d'ensemble déploiement
- **[DEPLOYMENT_DOCKER.md](deployment/DEPLOYMENT_DOCKER.md)** - Déploiement Docker complet
- **[FLY_DEPLOYMENT.md](deployment/FLY_DEPLOYMENT.md)** - Configuration Fly.io
- **[GANDI_DOMAIN_CONFIG.md](deployment/GANDI_DOMAIN_CONFIG.md)** - Configuration domaine

**Pour qui :** DevOps, Admin système, Développeurs senior

### 💻 Développement (`development/`)
Guides pour configurer l'environnement de développement.

**Contenu :**
- **[README.md](development/README.md)** - Setup environnement développement
- **[LOCAL_DEV.md](development/LOCAL_DEV.md)** - Configuration locale détaillée
- **[GIT_HOOKS.md](development/GIT_HOOKS.md)** - Hooks Git et qualité code

**Pour qui :** Développeurs, Contributeurs, Nouveaux arrivants

### 👥 Guide Utilisateur (`user-guide/`)
Documentation pour les utilisateurs finaux de la plateforme.

**Contenu :**
- **[README.md](user-guide/README.md)** - Guide utilisateur complet
- **[DOCUMENT_SYSTEM_GUIDE.md](user-guide/DOCUMENT_SYSTEM_GUIDE.md)** - Système de documents
- **[SEO_COMPLETE_GUIDE.md](user-guide/SEO_COMPLETE_GUIDE.md)** - Optimisation SEO

**Pour qui :** Employés ICTGROUP, Managers, RH, Utilisateurs finaux

### ⚙️ Technique (`technical/`)
Documentation technique avancée pour les développeurs et administrateurs.

**Contenu :**
- **[README.md](technical/README.md)** - Architecture et APIs
- **[PERFORMANCE_OPTIMIZATION.md](technical/PERFORMANCE_OPTIMIZATION.md)** - Optimisation
- **[SUPABASE_CONFIG.md](technical/SUPABASE_CONFIG.md)** - Configuration Supabase

**Pour qui :** Développeurs senior, Architectes, Admin BDD

## 🗂️ Documentation Historique

### 📋 Guides de Migration (Conservés)
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Guide migration générale
- **[MIGRATION_LEAVE_DATA.md](MIGRATION_LEAVE_DATA.md)** - Migration données congés
- **[MIGRATION_SUPABASE_SUCCESS.md](MIGRATION_SUPABASE_SUCCESS.md)** - Migration Supabase
- **[OVERTIME_MANAGEMENT.md](OVERTIME_MANAGEMENT.md)** - Gestion heures supplémentaires
- **[VALIDATION_RULES_CLARIFICATION.md](VALIDATION_RULES_CLARIFICATION.md)** - Règles validation

## 🔍 Documentation par Sujet

### 🏗️ Architecture et Infrastructure
- [Architecture technique](technical/README.md#architecture-technique)
- [Stack technologique](technical/README.md#stack-technologique)
- [Base de données](technical/README.md#base-de-données)
- [Configuration système](technical/README.md#configuration-système)

### 🚀 Déploiement et Production
- [Docker deployment](deployment/DEPLOYMENT_DOCKER.md)
- [Fly.io hosting](deployment/FLY_DEPLOYMENT.md)
- [Configuration domaine](deployment/GANDI_DOMAIN_CONFIG.md)
- [Monitoring production](deployment/README.md#monitoring)

### 💻 Développement
- [Environnement local](development/LOCAL_DEV.md)
- [Hooks Git](development/GIT_HOOKS.md)
- [Standards code](development/README.md#conventions-de-code)
- [Workflow développement](development/README.md#workflow-de-développement)

### 👥 Utilisation
- [Interface RH](user-guide/README.md#extranet-rh-complet)
- [Gestion congés](user-guide/README.md#gestion-des-congés)
- [Télétravail](user-guide/README.md#télétravail)
- [Système documents](user-guide/DOCUMENT_SYSTEM_GUIDE.md)

### ⚡ Performance et Optimisation
- [Optimisation Django](technical/PERFORMANCE_OPTIMIZATION.md)
- [Cache strategies](technical/README.md#performance-et-monitoring)
- [Database optimization](technical/README.md#optimisations-avancées)
- [Monitoring avancé](technical/README.md#métriques-clés)

## 🔄 Mise à Jour Documentation

### Contribution Documentation
```bash
# 1. Créer branche pour documentation
git checkout -b docs/update-user-guide

# 2. Modifier documentation
# Éditer les fichiers .md appropriés

# 3. Valider documentation
./docs/validate_docs.sh

# 4. Commit avec préfixe docs
git commit -m "docs: mettre à jour guide utilisateur"

# 5. Pull request
git push origin docs/update-user-guide
```

### Standards Documentation
- **Format** : Markdown avec extensions GitHub
- **Structure** : Hiérarchie claire avec table des matières
- **Images** : Optimisées et avec alt text
- **Liens** : Relatifs pour navigation interne
- **Code** : Blocs de code avec syntax highlighting
- **Emojis** : Pour améliorer la lisibilité

### Validation Documentation
```bash
# Script de validation automatique
./docs/validate_docs.sh

# Vérifications effectuées :
# ✅ Liens internes valides
# ✅ Structure Markdown correcte
# ✅ Images accessibles
# ✅ Table des matières à jour
# ✅ Orthographe française
```

## 📞 Aide et Support

### Problème avec la Documentation ?
- **🐛 Erreur trouvée** : [Créer une issue](https://github.com/ASaid-ASaid/ictgroup_website/issues)
- **📝 Amélioration** : [Suggérer modification](https://github.com/ASaid-ASaid/ictgroup_website/discussions)
- **❓ Question** : support@ictgroup.com

### Documentation Manquante ?
Si vous ne trouvez pas la documentation recherchée :

1. **Vérifiez l'index** ci-dessus pour navigation
2. **Utilisez la recherche** GitHub dans le repository
3. **Consultez les README** de chaque dossier
4. **Contactez l'équipe** si information critique manquante

---

## 🏆 Standards Documentation

Cette documentation suit les standards de l'industrie :
- **GitHub Flavored Markdown** pour compatibilité
- **Structure logique** par audience et usage
- **Navigation intuitive** avec liens internes
- **Exemples pratiques** avec code snippets
- **Maintenance régulière** avec validation automatique

*Dernière mise à jour : Août 2025*
