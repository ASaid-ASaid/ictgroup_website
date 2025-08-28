# 🚀 Documentation de Déploiement

Guides complets pour déployer ICTGROUP Website en production.

## 📁 Contenu

### 🐳 DEPLOYMENT_DOCKER.md
Guide complet du déploiement Docker
- Configuration conteneurs
- Docker Compose production
- Variables d'environnement
- Volumes et persistance

### 🛩️ FLY_DEPLOYMENT.md
Déploiement sur Fly.io
- Configuration Fly.io
- Secrets et variables
- Monitoring et logs
- Mise à l'échelle

### 🌐 GANDI_DOMAIN_CONFIG.md
Configuration domaine Gandi
- Paramétrage DNS
- Certificats SSL/TLS
- Redirection HTTPS
- Email et sous-domaines

## 🔧 Déploiement Rapide

### Production Standard
```bash
# 1. Configuration
cp .env.example .env
# Éditer .env avec vos variables

# 2. Docker local
docker-compose -f docker-compose.prod.yml up -d

# 3. Fly.io
./manage.sh deploy
```

### Variables Critiques
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🏗️ Architecture de Production

```mermaid
graph TB
    A[Internet] --> B[Cloudflare CDN]
    B --> C[Fly.io Load Balancer]
    C --> D[Django App Instances]
    D --> E[Supabase PostgreSQL]
    D --> F[Supabase Storage]
    D --> G[Redis Cache]
```

## 📊 Monitoring

### Métriques Clés
- Temps de réponse < 200ms
- Disponibilité > 99.9%
- Utilisation CPU < 80%
- Utilisation mémoire < 85%

### Outils
- Fly.io Monitoring
- Supabase Analytics
- Uptime monitoring
- Error tracking

## 🔒 Sécurité

### SSL/TLS
- Certificats automatiques (Let's Encrypt)
- HTTPS obligatoire
- HSTS headers
- Secure cookies

### Headers de Sécurité
- CSP (Content Security Policy)
- X-Frame-Options
- X-Content-Type-Options
- Referrer Policy

## 🔄 CI/CD Pipeline

### GitHub Actions
1. **Tests** : Unité, intégration, sécurité
2. **Build** : Image Docker optimisée
3. **Deploy** : Déploiement automatique
4. **Verify** : Tests post-déploiement

### Branches
- `main` → Production automatique
- `develop` → Staging automatique
- `feature/*` → Review apps

## 📋 Checklist Déploiement

### Pré-déploiement
- [ ] Tests passent en local
- [ ] Variables d'environnement configurées
- [ ] Base de données sauvegardée
- [ ] SSL/DNS configuré

### Post-déploiement
- [ ] Application accessible
- [ ] Tests fonctionnels OK
- [ ] Monitoring actif
- [ ] Logs sans erreurs

## 🆘 Dépannage

### Problèmes Courants
- Erreur 500 → Vérifier logs Django
- SSL invalide → Renouveler certificats
- DB connection → Vérifier DATABASE_URL
- Assets manquants → Relancer collectstatic

### Logs Utiles
```bash
# Fly.io
flyctl logs

# Docker local
docker-compose logs -f

# Django
tail -f logs/django.log
```
