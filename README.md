# 🏢 ICTGROUP Website

> **Plateforme web moderne pour ICTGROUP** - Site vitrine + Extranet RH avec Supabase

[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-blue.svg)](https://supabase.com/)
[![Fly.io](https://img.shields.io/badge/Deploy-Fly.io-purple.svg)](https://fly.io/)
[![Docker](https://img.shields.io/badge/Container-Docker-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

## 🎯 Fonctionnalités

### 🌐 Site Vitrine
- **Design moderne** : Interface responsive avec Tailwind CSS
- **Effets visuels** : Glass morphism et animations fluides
- **Performance** : Optimisations SEO et vitesse de chargement
- **Multilingue** : Support français/anglais

### 👥 Extranet RH
- **Gestion des employés** : Profils, rôles et permissions avancées
- **Système de congés** : Demandes, validation hiérarchique (Manager + RH)
- **Télétravail** : Planification et suivi des jours télétravail
- **Stock IT** : Gestion des équipements et matériel informatique
- **Dashboard** : Analytics et métriques en temps réel
- **Interface d'administration** : Gestion complète des utilisateurs et données

### 📊 Analytics (Supabase)
- **Logs d'activité** : Traçabilité des actions utilisateur
- **Notifications** : Système de notifications push
- **Métriques** : Performance et utilisation
- **Storage** : Gestion des documents et fichiers

## 🏗️ Architecture

```
ictgroup_website/
├── app/                    # Application Django
│   ├── extranet/          # Module extranet
│   ├── vitrine/           # Module site vitrine
│   └── ictgroup/          # Configuration Django
├── scripts/               # Scripts de gestion
├── tests/                 # Tests automatisés
├── docs/                  # Documentation
├── docker/                # Configuration Docker
├── config/                # Fichiers de configuration
└── manage.sh              # Script principal
```

### 🛠️ Stack Technique

- **Backend** : Django 4.2+ avec Python 3.12
- **Base de Données** : Supabase PostgreSQL
- **Frontend** : HTML5, Tailwind CSS, JavaScript vanilla
- **Cache** : Redis (via Supabase)
- **Storage** : Supabase Storage pour les fichiers
- **Deploy** : Fly.io avec Docker
- **Monitoring** : Logs intégrés Fly.io + Supabase

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
# Développement
./manage.sh start           # Démarrer l'environnement
./manage.sh stop            # Arrêter l'environnement
./manage.sh logs            # Voir les logs
./manage.sh shell           # Accéder au container

# Tests
./manage.sh test            # Exécuter tous les tests
./manage.sh test:unit       # Tests unitaires seulement
./manage.sh test:performance # Tests de performance

# Nettoyage
./manage.sh clean           # Nettoyage complet
./manage.sh clean:cache     # Cache seulement
./manage.sh clean:docker    # Docker seulement

# Déploiement
./manage.sh deploy          # Déployer sur Fly.io
./manage.sh deploy:check    # Vérifier la config

# Outils
./manage.sh health          # Vérifier l'état système
./manage.sh debug:static    # Diagnostiquer les fichiers statiques
```

### URLs de l'Application

| Service | URL | Description |
|---------|-----|-------------|
| **Site vitrine** | http://localhost:8000/ | Page d'accueil publique |
| **Extranet** | http://localhost:8000/extranet/ | Interface employés |
| **Admin Django** | http://localhost:8000/admin/ | Administration |
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

### Types de Tests

- **Tests unitaires** : Tests Django des modèles et vues
- **Tests d'intégration** : Tests de l'API Supabase
- **Tests de performance** : Métriques de temps de réponse
- **Tests de charge** : Simulation de trafic élevé

### Exécution des Tests

```bash
# Tous les tests
./manage.sh test

# Tests spécifiques
./manage.sh test:unit           # Django uniquement
./manage.sh test:performance    # Performance uniquement

# Coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 📚 Documentation

### Structure de la Documentation

- `docs/README.md` : Ce fichier
- `docs/DEPLOYMENT_DOCKER.md` : Guide Docker
- `docs/FLY_DEPLOYMENT.md` : Guide Fly.io
- `docs/SUPABASE_CONFIG.md` : Configuration Supabase
- `docs/MIGRATION_SUPABASE_SUCCESS.md` : Migration réussie
- `docs/PERFORMANCE_OPTIMIZATION.md` : Optimisations
- `docs/GANDI_DOMAIN_CONFIG.md` : Configuration domaine

### API Documentation

Les endpoints API sont documentés dans chaque vue Django avec des docstrings détaillées.

## 🤝 Contribution

### Workflow Git

```bash
# 1. Créer une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer et tester
./manage.sh test

# 3. Commit avec messages conventionnels
git commit -m "feat: ajouter système de notifications"

# 4. Push et créer une PR
git push origin feature/nouvelle-fonctionnalite
```

### Standards de Code

- **Python** : PEP 8 avec Black formatter
- **JavaScript** : ES6+ avec Prettier
- **CSS** : Tailwind CSS utility-first
- **Templates** : Django templates avec indentation 2 espaces

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
- **Email** : ahmed.said@ictgroup.com

## 📄 Licence

Ce projet est la propriété de **ICTGROUP** et est protégé par le droit d'auteur.

---

<div align="center">

**[🏠 Accueil](https://ictgroup-website.fly.dev/) • [📊 Dashboard](https://ictgroup-website.fly.dev/extranet/) • [⚙️ Admin](https://ictgroup-website.fly.dev/admin/)**

*Développé avec ❤️ par l'équipe ICTGROUP*

</div>
