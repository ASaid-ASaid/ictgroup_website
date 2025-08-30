# 🏢 ICTGROUP Website

> **Plateforme web moderne pour ICTGROUP** - Site vitrine + Extranet RH avec Supabase

[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-blue.svg)](https://supabase.com/)
[![Fly.io](https://img.shields.io/badge/Deploy-Fly.io-purple.svg)](https://fly.io/)
[![Docker](https://img.shields.io/badge/Container-Docker-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-green.svg)](tests/)

## 🚀 Démarrage Rapide

```bash
# Cloner le projet
git clone https://github.com/ASaid-ASaid/ictgroup_website.git
cd ictgroup_website

# Démarrer l'environnement de développement
./manage.sh start

# Accéder à l'application
open http://localhost:8000
```

## 📋 Table des Matières

- [🎯 Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [⚙️ Installation](#️-installation)
- [🚀 Utilisation](#-utilisation)
- [📊 Base de Données](#-base-de-données)
- [🔧 Configuration](#-configuration)
- [📦 Déploiement](#-déploiement)
- [🧪 Tests](#-tests)
- [📚 Documentation](#-documentation)
- [📁 Structure du Projet](#-structure-du-projet)

## 🎯 Fonctionnalités

### 🌐 Site Vitrine
- **Design moderne** : Interface responsive avec Tailwind CSS
- **Effets visuels** : Glass morphism et animations fluides
- **Performance** : Optimisations SEO et vitesse de chargement
- **Multilingue** : Support français/anglais

### 👥 Extranet RH Complet
- **Gestion des employés** : Profils, rôles et permissions avancées
- **Système de congés** : Demandes, validation hiérarchique (Manager + RH)
- **Télétravail** : Planification et suivi des jours télétravail
- **Heures supplémentaires** : Gestion weekend et validation
- **Documents** : Upload sécurisé avec permissions granulaires
- **Dashboard** : Analytics et métriques en temps réel
- **Notifications** : Système d'alertes automatiques
- **Rapports** : Génération PDF/Excel des statistiques
- **Mobile-first** : Interface optimisée mobile et desktop

### 🏢 Intranet Administratif
- **Gestion des factures** : Création, suivi et paiement des factures clients
- **Trésorerie** : Enregistrement des recettes/dépenses et virements
- **Bons de commande** : Gestion des achats fournisseurs et livraisons
- **Pièces jointes** : Documents sécurisés (contrats, devis, reçus)
- **Tableaux de bord** : Métriques financières et statistiques
- **Accès restreint** : Réservé aux administrateurs uniquement

### 📊 Analytics Avancés (Supabase)
- **Logs d'activité** : Traçabilité complète des actions
- **Métriques RH** : Statistiques d'utilisation et performance
- **Notifications temps réel** : WebSocket avec Supabase Realtime
- **Storage sécurisé** : Gestion documents avec permissions

## 🏗️ Architecture

### Structure du Projet
```
ictgroup_website/
├── 🐍 app/                     # Application Django principale
│   ├── extranet/              # Module RH (congés, télétravail, users)
│   ├── intranet/              # Module administratif (factures, trésorerie)
│   ├── vitrine/               # Site vitrine public
│   ├── ictgroup/              # Configuration Django
│   └── static/                # Fichiers statiques
├── 📜 scripts/                # Scripts organisés par catégorie
│   ├── deployment/            # Scripts de déploiement (Fly.io, domaine)
│   ├── testing/               # Scripts de test et CI
│   ├── maintenance/           # Scripts de maintenance et monitoring
│   └── development/           # Scripts de développement (hooks Git)
├── 🧪 tests/                  # Tests organisés par type
│   ├── unit/                  # Tests unitaires rapides
│   ├── integration/           # Tests d'intégration
│   ├── performance/           # Tests de performance
│   └── functional/            # Tests fonctionnels end-to-end
├── 📚 docs/                   # Documentation structurée
│   ├── deployment/            # Guides de déploiement
│   ├── development/           # Guides de développement
│   ├── user-guide/            # Documentation utilisateur
│   └── technical/             # Documentation technique
├── 🗂️ archive/                # Fichiers archivés (nettoyage)
│   ├── temp_files/            # Scripts temporaires archivés
│   └── docs_deprecated/       # Documentation obsolète
├── 🐳 docker/                 # Configuration Docker
├── ⚙️ config/                 # Fichiers de configuration
├── 📊 logs/                   # Logs d'application
├── 🔄 migration_data/         # Données de migration
└── 📋 manage.sh               # Script principal de gestion
```

### 🛠️ Stack Technique

- **Backend** : Django 5.2.5 avec Python 3.12
- **Base de Données** : Supabase PostgreSQL avec fonctions avancées
- **Frontend** : Tailwind CSS 3.x, JavaScript ES6+ vanilla
- **Cache** : Redis via Supabase pour optimisation performance
- **Storage** : Supabase Storage pour documents sécurisés
- **Deploy** : Fly.io avec Docker optimisé
- **Monitoring** : Logs intégrés Fly.io + Supabase Analytics
- **CI/CD** : GitHub Actions avec tests automatisés

## ⚙️ Installation

### Prérequis

- Docker et Docker Compose
- Git
- Compte Supabase (gratuit)
- Compte Fly.io (optionnel pour le déploiement)

### Installation automatique

```bash
# 1. Cloner le repository
git clone https://github.com/ASaid-ASaid/ictgroup_website.git
cd ictgroup_website

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés Supabase

# 3. Démarrer l'application
./manage.sh start
```

### Installation manuelle

<details>
<summary>Voir les étapes détaillées</summary>

```bash
# 1. Construire l'image Docker
docker-compose build

# 2. Démarrer les services
docker-compose up -d

# 3. Exécuter les migrations
./manage.sh migrate

# 4. Créer un superutilisateur
./manage.sh superuser
```

</details>

## 🚀 Utilisation

### Script de Gestion Principal

Le script `./manage.sh` centralise toutes les opérations :

```bash
# 🚀 Développement
./manage.sh start           # Démarrer l'environnement complet
./manage.sh stop            # Arrêter tous les services
./manage.sh restart         # Redémarrer avec rechargement
./manage.sh logs            # Voir les logs en temps réel
./manage.sh shell           # Accéder au container Django

# 🧪 Tests et Qualité
./manage.sh test            # Exécuter tous les tests
./manage.sh test:unit       # Tests unitaires uniquement
./manage.sh test:integration # Tests d'intégration
./manage.sh test:performance # Tests de performance
./manage.sh test:coverage   # Tests avec couverture de code
./manage.sh lint            # Vérification qualité code
./manage.sh format          # Formatage automatique (Black, Prettier)

# 🧹 Nettoyage et Maintenance
./manage.sh clean           # Nettoyage complet (cache, logs, Docker)
./manage.sh clean:cache     # Cache Django uniquement
./manage.sh clean:docker    # Images et containers Docker
./manage.sh clean:logs      # Anciens fichiers de logs
./manage.sh optimize        # Optimisation complète du projet

# 🚀 Déploiement
./manage.sh deploy          # Déploiement automatique Fly.io
./manage.sh deploy:check    # Vérification configuration déploiement
./manage.sh deploy:staging  # Déploiement environnement staging

# 🔧 Outils de Développement
./manage.sh setup:dev       # Configuration environnement développement
./manage.sh migrate         # Migrations base de données
./manage.sh superuser       # Créer utilisateur administrateur
./manage.sh collectstatic   # Collecter fichiers statiques
./manage.sh backup          # Sauvegarde base de données

# 📊 Monitoring et Debug
./manage.sh health          # Vérifier l'état système complet
./manage.sh debug:db        # Diagnostiquer problèmes base de données
./manage.sh debug:static    # Diagnostiquer fichiers statiques
./manage.sh debug:performance # Analyser performance de l'application
```

### URLs de l'Application

| Service | URL | Description |
|---------|-----|-------------|
| **Site vitrine** | http://localhost:8000/ | Page d'accueil publique |
| **Extranet** | http://localhost:8000/extranet/ | Interface employés |
| **Intranet** | http://localhost:8000/intranet/ | Administration (réservé admins) |
| **Admin Django** | http://localhost:8000/admin/ | Administration système |
| **Production** | https://ictgroup-website.fly.dev/ | Site en production |

## 📊 Base de Données

### Configuration Supabase

```bash
# 1. Créer un projet sur https://supabase.com
# 2. Récupérer les clés dans Settings > API
# 3. Configurer les variables d'environnement

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Tables Principales

- **Django Standard** : Users, Groups, Permissions
- **Extranet** : UserProfile, LeaveRequest, TeleworkRequest, StockItem
- **Intranet** : Invoice, Treasury, PurchaseOrder, Attachment
- **Analytics** : user_activity_logs, notifications, performance_metrics

### Migration

```bash
# Appliquer les migrations Django
./manage.sh migrate

# Créer les tables analytics Supabase (optionnel)
# Exécuter config/supabase_setup.sql dans le dashboard Supabase
```

## 🔧 Configuration

### Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DEBUG` | Mode debug Django | `True` |
| `SUPABASE_URL` | URL du projet Supabase | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Clé publique Supabase | `eyJ...` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://...` |

### Fichiers de Configuration

- `config/fly.toml` : Configuration Fly.io
- `config/supabase_setup.sql` : Tables analytics Supabase
- `.env.example` : Template des variables d'environnement
- `docker-compose.yml` : Configuration Docker

## 📦 Déploiement

### Fly.io (Production)

```bash
# 1. Installer Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Se connecter
flyctl auth login

# 3. Déployer
./manage.sh deploy

# 4. Configurer les secrets
flyctl secrets set SUPABASE_URL=https://your-project.supabase.co
flyctl secrets set SUPABASE_ANON_KEY=your-anon-key
flyctl secrets set DATABASE_URL=postgresql://...
```

### Docker (Local/Production)

```bash
# Production Docker
docker-compose -f docker-compose.prod.yml up -d

# Surveillance
docker-compose logs -f
```

## 🧪 Tests

### Structure des Tests

```bash
tests/
├── unit/              # 🔬 Tests unitaires (Models, Forms, Utils)
├── integration/       # 🔗 Tests d'intégration (Views, API, Auth)
├── performance/       # ⚡ Tests de performance (Response time, DB queries)
└── functional/        # 🎭 Tests fonctionnels (User journeys, E2E)
```

### Exécution des Tests

```bash
# Suite complète de tests
./manage.sh test                    # Tous les tests avec rapport

# Tests par catégorie
./manage.sh test:unit              # < 30s - Tests rapides isolés
./manage.sh test:integration       # < 2min - Tests interaction composants
./manage.sh test:performance       # < 5min - Benchmarks et métriques
./manage.sh test:functional        # < 10min - Parcours utilisateur complets

# Tests avec métriques
./manage.sh test:coverage          # Couverture de code (objectif: >85%)
./manage.sh test:security          # Analyse sécurité avec bandit
./manage.sh test:load              # Tests de charge avec Artillery

# Tests spécifiques
python manage.py test tests.unit.test_models
python manage.py test tests.integration.test_views::LeaveViewTest
```

### Métriques de Qualité

| Type de Test | Objectif Couverture | Temps Max | Status |
|--------------|-------------------|-----------|---------|
| **Unit Tests** | > 90% | < 30s | ✅ Passing |
| **Integration Tests** | > 80% | < 2min | ✅ Passing |
| **Performance Tests** | Benchmarks | < 5min | ✅ Passing |
| **Global Coverage** | > 85% | - | ✅ 85%+ |

### Outils de Test

- **Django TestCase** : Base des tests unitaires
- **pytest-django** : Fonctionnalités avancées et fixtures
- **Coverage.py** : Mesure couverture de code
- **Artillery.js** : Tests de charge HTTP
- **Selenium** : Tests navigateur (fonctionnels)
- **Factory Boy** : Génération données de test

## 📚 Documentation

### Structure Documentation Organisée

La documentation est maintenant organisée par domaine d'expertise :

```bash
docs/
├── 🚀 deployment/         # Guides de déploiement production
│   ├── README.md         # Overview déploiement
│   ├── DEPLOYMENT_DOCKER.md
│   ├── FLY_DEPLOYMENT.md
│   └── GANDI_DOMAIN_CONFIG.md
├── 💻 development/        # Guides développement
│   ├── README.md         # Setup environnement dev
│   ├── LOCAL_DEV.md
│   └── GIT_HOOKS.md
├── 👥 user-guide/         # Documentation utilisateur final
│   ├── README.md         # Guide utilisateur complet
│   ├── DOCUMENT_SYSTEM_GUIDE.md
│   └── SEO_COMPLETE_GUIDE.md
├── ⚙️ technical/          # Documentation technique avancée
│   ├── README.md         # Architecture et APIs
│   ├── PERFORMANCE_OPTIMIZATION.md
│   └── SUPABASE_CONFIG.md
├── 📋 INDEX.md           # Table des matières principale
└── 🔗 MIGRATION_*.md     # Guides de migration (conservés)
```

### Navigation Rapide

| Rôle | Documentation Recommandée |
|------|---------------------------|
| **🆕 Nouveau Développeur** | [`docs/development/`](docs/development/) |
| **🚀 DevOps/Déploiement** | [`docs/deployment/`](docs/deployment/) |
| **👤 Utilisateur Final** | [`docs/user-guide/`](docs/user-guide/) |
| **🔧 Administrateur Système** | [`docs/technical/`](docs/technical/) |

### Documentation Interactive

- **API Documentation** : Endpoints documentés avec exemples
- **Code Comments** : Docstrings Python détaillées
- **Database Schema** : ERD avec relations
- **Architecture Diagrams** : Mermaid.js intégrés

## 📁 Structure du Projet

### Architecture Organisée

```
ictgroup_website/
├── 🐍 app/                     # Application Django principale
│   ├── extranet/              # Module RH (congés, télétravail, users)
│   ├── vitrine/               # Site vitrine public
│   ├── ictgroup/              # Configuration Django
│   └── static/                # Fichiers statiques
├── 📜 scripts/                # Scripts organisés par catégorie
│   ├── deployment/            # Scripts de déploiement (Fly.io, domaine)
│   ├── testing/               # Scripts de test et CI
│   ├── maintenance/           # Scripts de maintenance et monitoring
│   └── development/           # Scripts de développement (hooks Git)
├── 🧪 tests/                  # Tests organisés par type
│   ├── unit/                  # Tests unitaires rapides
│   ├── integration/           # Tests d'intégration
│   ├── performance/           # Tests de performance
│   └── functional/            # Tests fonctionnels end-to-end
├── 📚 docs/                   # Documentation structurée
│   ├── deployment/            # Guides de déploiement
│   ├── development/           # Guides de développement
│   ├── user-guide/            # Documentation utilisateur
│   └── technical/             # Documentation technique
├── 🗂️ archive/                # Fichiers archivés (nettoyage)
│   ├── temp_files/            # Scripts temporaires archivés
│   └── docs_deprecated/       # Documentation obsolète
├── 🐳 docker/                 # Configuration Docker
├── ⚙️ config/                 # Fichiers de configuration
├── 📊 logs/                   # Logs d'application
├── 🔄 migration_data/         # Données de migration
└── 📋 manage.sh               # Script principal de gestion
```

### Organisation par Responsabilités

| Dossier | Responsabilité | Audience | Contenu |
|---------|----------------|----------|---------|
| **`scripts/deployment/`** | Déploiement | DevOps | Scripts Fly.io, Docker, domaine |
| **`scripts/testing/`** | Tests & CI | Équipe dev | Tests automatisés, couverture |
| **`scripts/maintenance/`** | Maintenance | Admin sys | Sauvegarde, monitoring, nettoyage |
| **`scripts/development/`** | Développement | Développeurs | Hooks Git, setup dev |
| **`docs/deployment/`** | Déploiement | DevOps | Guides production, configuration |
| **`docs/development/`** | Développement | Développeurs | Setup local, bonnes pratiques |
| **`docs/user-guide/`** | Utilisation | Utilisateurs | Guides fonctionnels, FAQ |
| **`docs/technical/`** | Architecture | Tech leads | APIs, performance, sécurité |
| **`tests/unit/`** | Tests rapides | CI/CD | Tests isolés, couverture élevée |
| **`tests/integration/`** | Tests complets | QA | Tests composants, workflows |
| **`tests/performance/`** | Performance | DevOps | Benchmarks, métriques |
| **`tests/functional/`** | E2E | Product | Parcours utilisateur complets |

### Avantages de l'Architecture

1. **📁 Séparation claire** : Chaque type de fichier dans son dossier approprié
2. **🔍 Navigation facile** : README dans chaque dossier pour guider
3. **🧹 Maintenance réduite** : Structure organisée et propre
4. **📚 Documentation structurée** : Par audience (dev, ops, utilisateur)
5. **🧪 Tests organisés** : Par complexité et type
6. **📜 Scripts classés** : Par usage (déploiement, maintenance, etc.)

### Workflow de Développement

- **Nouveau développeur** : Accès rapide via `docs/development/`
- **Tests** : Exécution ciblée par type (`./manage.sh test:unit`)
- **Déploiement** : Scripts centralisés dans `scripts/deployment/`
- **Maintenance** : Outils dans `scripts/maintenance/`
- **Documentation** : Structure logique par rôle utilisateur

## 🐛 Dépannage

### Problèmes Courants

<details>
<summary>Docker ne démarre pas</summary>

```bash
# Vérifier Docker
docker --version
docker info

# Redémarrer Docker
sudo systemctl restart docker

# Nettoyer et redémarrer
./manage.sh clean:docker
./manage.sh start
```

</details>

<details>
<summary>Erreur de base de données</summary>

```bash
# Vérifier la connexion Supabase
./manage.sh shell
python manage.py dbshell

# Re-migrer
./manage.sh migrate
```

</details>

<details>
<summary>Fichiers statiques non chargés</summary>

```bash
# Diagnostiquer
./manage.sh debug:static

# Recollect
docker-compose exec web python manage.py collectstatic --clear
```

</details>

## 📞 Support

- **Issues GitHub** : [github.com/ASaid-ASaid/ictgroup_website/issues](https://github.com/ASaid-ASaid/ictgroup_website/issues)
- **Documentation** : Dossier `docs/`
- **Email** : support@ictgroup.com

## 📄 Licence

Ce projet est la propriété de **ICTGROUP** et est protégé par le droit d'auteur.

---

<div align="center">

## 🤝 Contribution

### Workflow Git Optimisé

```bash
# 1. Configuration environnement développement
./manage.sh setup:dev              # Installation hooks Git + dépendances

# 2. Créer une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# 3. Développement avec qualité automatique
./manage.sh format                 # Formatage Black + Prettier
./manage.sh lint                   # Vérification qualité code
./manage.sh test:unit              # Tests rapides

# 4. Commit avec standards (hooks automatiques)
git commit -m "feat: ajouter système de notifications"
# → Pre-commit hook : formatage + linting + tests

# 5. Tests complets avant push
./manage.sh test                   # Suite complète de tests
git push origin feature/nouvelle-fonctionnalite
# → Pre-push hook : tests + sécurité

# 6. Pull Request avec CI/CD automatique
# → GitHub Actions : tests + déploiement staging
```

### Standards de Code Automatisés

#### Python/Django
- **PEP 8** strict avec Black formatter
- **Type hints** obligatoires (mypy)
- **Import sorting** avec isort  
- **Docstrings** pour toutes les fonctions publiques
- **Tests** pour chaque vue/model avec couverture >90%

#### JavaScript/Frontend
- **ES6+** syntax moderne
- **Prettier** formatting automatique
- **ESLint** configuration stricte
- **JSDoc** documentation des fonctions

#### Templates/CSS
- **Tailwind CSS** utility-first approach
- **Mobile-first** responsive design obligatoire
- **Semantic HTML5** avec accessibility (WCAG 2.1)
- **Django templates** avec blocks structurés

### Conventional Commits

```bash
# Types de commits standardisés
feat: ajouter système de notifications          # Nouvelle fonctionnalité
fix: corriger validation formulaire congés      # Correction bug
docs: mettre à jour README et architecture      # Documentation
style: formatter code Python avec Black        # Style code
refactor: optimiser requêtes base données       # Refactoring
test: ajouter tests unitaires LeaveRequest     # Tests
perf: améliorer temps réponse dashboard        # Performance
ci: configurer GitHub Actions déploiement      # CI/CD

# Exemples avec scope
feat(extranet): ajouter validation télétravail
fix(auth): corriger redirection après login
docs(api): documenter endpoints REST
```

## 📞 Support et Communauté

### Contact
- **📧 Email** : support@ictgroup.com
- **🐛 Issues GitHub** : [Signaler un bug](https://github.com/ASaid-ASaid/ictgroup_website/issues)
- **💡 Feature Requests** : [Nouvelle fonctionnalité](https://github.com/ASaid-ASaid/ictgroup_website/discussions)
- **📚 Documentation** : [Guides complets](docs/)

### Ressources Utiles
- **📚 Formation Django** : [Documentation officielle](https://docs.djangoproject.com/)
- **🎨 Tailwind CSS** : [Composants et exemples](https://tailwindcss.com/)
- **🗄️ Supabase** : [Documentation API](https://supabase.com/docs)
- **🚀 Fly.io** : [Guides de déploiement](https://fly.io/docs/)

---

**[🏠 Site Vitrine](https://ictgroup-website.fly.dev/) • [📊 Extranet RH](https://ictgroup-website.fly.dev/extranet/) • [⚙️ Administration](https://ictgroup-website.fly.dev/admin/)**

*Développé avec ❤️ par l'équipe ICTGROUP*

</div>

## 📄 Licence

Ce projet est la propriété de **ICTGROUP** et est protégé par le droit d'auteur.

Tous droits réservés © 2025 ICTGROUP
