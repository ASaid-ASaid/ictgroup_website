# 🚀 Scripts de Déploiement

Scripts pour le déploiement en production et la configuration des services.

## 📁 Contenu

### 🛩️ deploy_fly.sh
Déploiement automatisé sur Fly.io
- Configuration des secrets
- Déploiement avec vérifications
- Tests post-déploiement

### 🌐 configure_gandi_domain.sh
Configuration du domaine Gandi
- Configuration DNS
- Certificats SSL
- Redirection HTTPS

### 🔐 setup-github-secrets.sh
Configuration des secrets GitHub Actions
- Variables d'environnement CI/CD
- Clés de déploiement
- Tokens d'accès

## 🔧 Utilisation

```bash
# Déploiement complet
./manage.sh deploy

# Déploiement Fly.io uniquement
./scripts/deployment/deploy_fly.sh

# Configuration domaine
./scripts/deployment/configure_gandi_domain.sh

# Setup CI/CD
./scripts/deployment/setup-github-secrets.sh
```

## 📋 Prérequis

- Compte Fly.io configuré
- Domaine Gandi configuré
- Repository GitHub avec Actions
- Variables d'environnement définies

## ⚠️ Notes Importantes

- Toujours tester en local avant le déploiement
- Sauvegarder la base de données avant mise à jour
- Vérifier les certificats SSL après déploiement
