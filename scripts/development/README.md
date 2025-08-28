# 💻 Scripts de Développement

Scripts pour faciliter le développement et maintenir la qualité du code.

## 📁 Contenu

### 🎣 install-git-hooks.sh
Installation des hooks Git
- Pre-commit : formatage code
- Pre-push : tests automatiques
- Commit-msg : validation messages

### 📝 prepare_commit.sh
Préparation des commits
- Formatage automatique (Black, Prettier)
- Vérification linting
- Tests rapides
- Génération changelog

## 🔧 Utilisation

```bash
# Installation hooks Git
./scripts/development/install-git-hooks.sh

# Préparation commit
./scripts/development/prepare_commit.sh

# Via manage.sh
./manage.sh setup:dev    # Installation complète environnement dev
./manage.sh lint         # Vérification code
./manage.sh format       # Formatage automatique
```

## 🔍 Vérifications Automatiques

### Pre-commit
- Formatage Python (Black)
- Formatage JavaScript (Prettier)
- Vérification imports Python (isort)
- Linting (flake8, ESLint)
- Tests unitaires rapides

### Pre-push
- Suite complète de tests
- Vérification couverture code
- Validation sécurité
- Scan dépendances

### Commit-msg
- Format conventional commits
- Longueur message
- Références issues

## 📋 Configuration

### Outils Requis
- Black (formatage Python)
- isort (imports Python)
- flake8 (linting Python)
- Prettier (formatage JS/CSS)
- ESLint (linting JavaScript)

### Installation
```bash
# Python tools
pip install black isort flake8 bandit safety

# Node.js tools (si applicable)
npm install -g prettier eslint
```

## 🎯 Standards de Code

### Python
- PEP 8 (via Black)
- Imports organisés (isort)
- Type hints recommandés
- Docstrings obligatoires

### JavaScript
- ES6+ syntax
- Prettier formatting
- ESLint configuration
- JSDoc pour documentation

### Django
- Class-based views préférées
- Serializers pour API
- Tests pour chaque vue
- Documentation des models

## 🚀 Workflow Recommandé

1. **Développement** : Code avec hooks activés
2. **Commit** : Messages conventional commits
3. **Push** : Tests automatiques validés
4. **PR** : Review + tests CI
5. **Merge** : Déploiement automatique
