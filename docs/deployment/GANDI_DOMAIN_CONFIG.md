# Configuration domaine Gandi pour Fly.io

## 🌐 Connecter votre domaine Gandi à Fly.io

### 1. Configurer les certificats SSL sur Fly.io

```bash
# Remplacez par votre vrai domaine
flyctl certs create votre-domaine.com
flyctl certs create www.votre-domaine.com
```

### 2. Configuration DNS dans votre interface Gandi

Connectez-vous à [admin.gandi.net](https://admin.gandi.net) et configurez :

**Pour le domaine principal :**
```
Type: A
Nom: @
Valeur: [IP donnée par Fly.io]
TTL: 300
```

**Pour le sous-domaine www :**
```
Type: CNAME
Nom: www
Valeur: ictgroup-website.fly.dev
TTL: 300
```

### 3. Obtenir l'IP de Fly.io

```bash
flyctl ips list
```

### 4. Vérifier la configuration

```bash
# Vérifier les certificats
flyctl certs show votre-domaine.com

# Tester la résolution DNS
nslookup votre-domaine.com
```

### 5. Mettre à jour les ALLOWED_HOSTS

Dans `app/ictgroup/settings.py` :

```python
ALLOWED_HOSTS = [
    "ictgroup-website.fly.dev", 
    ".fly.dev", 
    "votre-domaine.com",
    "www.votre-domaine.com",
    "localhost", 
    "127.0.0.1"
]
```

### 6. Redéployer

```bash
flyctl deploy
```

## ✅ Résultat final

Votre site sera accessible sur :
- `https://votre-domaine.com` (votre domaine principal)
- `https://www.votre-domaine.com` (avec www)
- `https://ictgroup-website.fly.dev` (domaine Fly.io de secours)

## 🔧 Script automatique de configuration

```bash
#!/bin/bash
# configure_domain.sh

echo "🌐 Configuration domaine Gandi + Fly.io"

read -p "Entrez votre nom de domaine (ex: ictgroup.fr): " DOMAIN

echo "📝 Configuration des certificats SSL..."
flyctl certs create $DOMAIN
flyctl certs create www.$DOMAIN

echo "📋 Configuration DNS à faire dans Gandi :"
echo "========================================"
echo ""
echo "1. Type: A"
echo "   Nom: @"
echo "   Valeur: $(flyctl ips list | grep 'v4' | awk '{print $2}' | head -1)"
echo "   TTL: 300"
echo ""
echo "2. Type: CNAME"
echo "   Nom: www"
echo "   Valeur: ictgroup-website.fly.dev"
echo "   TTL: 300"
echo ""
echo "✅ Configurez ces DNS dans votre interface Gandi"
echo "🔄 La propagation DNS prend 5-30 minutes"

# Mettre à jour settings.py
echo "🔧 Mise à jour des ALLOWED_HOSTS..."
# Ici vous pouvez ajouter la logique pour modifier settings.py

echo "🚀 Redéploiement..."
flyctl deploy

echo "✅ Configuration terminée !"
echo "🌐 Votre site sera disponible sur https://$DOMAIN"
```
