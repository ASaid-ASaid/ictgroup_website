# 💻 Documentation de Développement

Guides pour configurer l'environnement de développement et contribuer au projet.

## 📁 Contenu

### 🏠 LOCAL_DEV.md
Configuration environnement local
- Installation dépendances
- Configuration base de données
- Variables d'environnement
- Debugging Django

### 🎣 GIT_HOOKS.md
Configuration des hooks Git
- Pre-commit hooks
- Standards de code
- Workflow Git
- Messages de commit

## 🚀 Démarrage Rapide

### Installation
```bash
# 1. Cloner le projet
git clone https://github.com/ASaid-ASaid/ictgroup_website.git
cd ictgroup_website

# 2. Configuration automatique
./manage.sh setup:dev

# 3. Démarrer le serveur
./manage.sh start
```

### Configuration Manuelle
```bash
# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dépendances
pip install -r requirements-dev.txt

# Base de données
./manage.sh migrate
./manage.sh superuser

# Hooks Git
./scripts/development/install-git-hooks.sh
```

## 🏗️ Architecture de Développement

### Structure du Projet
```
ictgroup_website/
├── app/                    # Application Django
│   ├── extranet/          # Module RH
│   ├── vitrine/           # Site vitrine
│   └── ictgroup/          # Configuration
├── scripts/               # Scripts utilitaires
├── tests/                 # Tests automatisés
├── docs/                  # Documentation
└── docker/               # Configuration Docker
```

### Stack Technique
- **Backend** : Django 5.2.5 + Python 3.12
- **Frontend** : Tailwind CSS + JavaScript vanilla
- **Database** : Supabase PostgreSQL
- **Cache** : Redis (Supabase)
- **Storage** : Supabase Storage

## 🧪 Tests et Qualité

### Lancement des Tests
```bash
# Tous les tests
./manage.sh test

# Par catégorie
./manage.sh test:unit
./manage.sh test:integration
./manage.sh test:performance

# Avec couverture
./manage.sh test:coverage
```

### Standards de Code
```bash
# Formatage automatique
./manage.sh format

# Vérification linting
./manage.sh lint

# Analyse sécurité
./manage.sh security
```

### Coverage Objectifs
- **Tests unitaires** : > 90%
- **Tests d'intégration** : > 80%
- **Couverture globale** : > 85%

## 🔧 Outils de Développement

### IDE Recommandés
- **VS Code** avec extensions Python/Django
- **PyCharm Professional**
- **Vim/Neovim** avec plugins Python

### Extensions VS Code
- Python
- Django
- Tailwind CSS IntelliSense
- GitLens
- Docker

### Debug Django
```python
# settings.py (local)
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Toolbar Django Debug
INTERNAL_IPS = ['127.0.0.1']
```

## 📝 Conventions de Code

### Python/Django
- **PEP 8** strict (Black formatting)
- **Type hints** obligatoires
- **Docstrings** pour toutes les fonctions
- **Tests** pour chaque vue/model

### JavaScript
- **ES6+** syntax
- **Prettier** formatting
- **JSDoc** documentation
- **Modules ES6** importés

### CSS/HTML
- **Tailwind CSS** utility-first
- **Mobile-first** responsive
- **Semantic HTML5**
- **Accessibility** WCAG 2.1

### Commits
```bash
# Format conventional commits
feat: ajouter système de notifications
fix: corriger validation formulaire
docs: mettre à jour README
style: formatter code Python
refactor: optimiser requêtes DB
test: ajouter tests unitaires
```

## 🔄 Workflow de Développement

### 1. Feature Development
```bash
# Créer branche feature
git checkout -b feature/nouvelle-fonctionnalite

# Développer avec tests
./manage.sh test

# Commits conventionnels
git commit -m "feat: ajouter nouvelle fonctionnalité"
```

### 2. Code Review
- Tests automatiques ✅
- Review par un pair ✅
- Documentation à jour ✅
- Standards respectés ✅

### 3. Intégration
```bash
# Rebase sur main
git rebase main

# Push et PR
git push origin feature/nouvelle-fonctionnalite
```

## 🚨 Debugging

### Django Debug Toolbar
```python
# Installation
pip install django-debug-toolbar

# Configuration automatique en mode DEBUG
```

### Logs de Développement
```bash
# Django logs
tail -f app/django.log

# Performance logs
tail -f app/performance.log

# Supabase logs (via dashboard)
```

### Problèmes Courants

#### Port déjà utilisé
```bash
./manage.sh stop
./manage.sh start
```

#### Problèmes de migration
```bash
./manage.sh reset:db
./manage.sh migrate
```

#### Cache problématique
```bash
./manage.sh clean:cache
```

## 📚 Ressources

### Documentation Django
- [Django Official Docs](https://docs.djangoproject.com/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

### Supabase
- [Supabase Docs](https://supabase.com/docs)
- [Python Client](https://supabase.com/docs/reference/python)

### Frontend
- [Tailwind CSS](https://tailwindcss.com/docs)
- [MDN Web Docs](https://developer.mozilla.org/)
