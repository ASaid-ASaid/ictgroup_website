# Configuration Fly.io pour ICT Group Website

## 📋 Prérequis

1. **Compte Fly.io** : Créez un compte sur [fly.io](https://fly.io)
2. **Fly CLI** : Installé automatiquement par le script de déploiement
3. **Docker** : Optionnel (Fly.io utilise des buildpacks)

## 🚀 Déploiement rapide

### Option 1 : Script automatique
```bash
./manage.sh deploy:fly
```

### Option 2 : Déploiement manuel

1. **Installer Fly CLI** :
```bash
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"
```

2. **Se connecter à Fly.io** :
```bash
flyctl auth login
```

3. **Lancer l'application** :
```bash
flyctl launch
```

4. **Créer une base de données PostgreSQL** :
```bash
flyctl postgres create --name ictgroup-db --region cdg
flyctl postgres attach ictgroup-db
```

5. **Configurer les variables d'environnement** :
```bash
flyctl secrets set DJANGO_SECRET_KEY="votre-cle-secrete-django"
flyctl secrets set DEBUG=False
```

6. **Déployer** :
```bash
flyctl deploy
```

## 🔧 Configuration

### Variables d'environnement requises

- `DJANGO_SECRET_KEY` : Clé secrète Django (générez-en une nouvelle)
- `DATABASE_URL` : Configurée automatiquement par Fly.io
- `DEBUG` : Mettre à `False` en production

### Génération d'une clé secrète Django

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📊 Monitoring et logs

```bash
# Voir les logs en temps réel
flyctl logs

# Status de l'application
flyctl status

# Voir les métriques
flyctl metrics

# Se connecter à la base de données
flyctl postgres connect -a ictgroup-db
```

## 🔄 Mise à jour

Pour mettre à jour l'application :
```bash
flyctl deploy
```

## 🌐 URLs importantes

- **Application** : https://ictgroup-website.fly.dev
- **Admin Django** : https://ictgroup-website.fly.dev/admin/
- **Health check** : https://ictgroup-website.fly.dev/health/

## 📝 Notes importantes

1. **Fichiers statiques** : Gérés par WhiteNoise en production
2. **Base de données** : PostgreSQL hébergée sur Fly.io
3. **SSL/TLS** : Automatiquement configuré par Fly.io
4. **Scaling** : Configuré pour auto-start/stop selon le trafic
5. **Région** : CDG (Paris) pour une latence minimale en Europe

## 🛠️ Dépannage

### Problèmes courants

1. **Erreur de migration** :
```bash
flyctl ssh console
cd app && python manage.py migrate
```

2. **Fichiers statiques manquants** :
```bash
flyctl ssh console
cd app && python manage.py collectstatic --noinput
```

3. **Logs d'erreur** :
```bash
flyctl logs --app ictgroup-website
```

## 💰 Coûts

- **Application** : Gratuit jusqu'à 3 machines
- **Base de données** : ~5$/mois pour PostgreSQL
- **Bande passante** : Généreuse allocation gratuite

## 🔐 Sécurité

- HTTPS forcé automatiquement
- Variables d'environnement chiffrées
- Réseau privé entre l'app et la DB
- Firewall automatique
