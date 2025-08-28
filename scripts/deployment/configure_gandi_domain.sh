#!/bin/bash
# configure_gandi_domain.sh
# Script pour configurer un domaine Gandi avec Fly.io

set -e

echo "🌐 Configuration domaine Gandi + Fly.io"
echo "======================================="

# Variables
FLY_APP="ictgroup-website"
FLY_IPV4="66.241.125.26"
FLY_IPV6="2a09:8280:1::92:8ac4:0"
FLY_DOMAIN="ictgroup-website.fly.dev"

# Demander le domaine
if [ -z "$1" ]; then
    read -p "Entrez votre nom de domaine (ex: ictgroup.fr): " DOMAIN
else
    DOMAIN="$1"
fi

echo ""
echo "📝 Configuration pour le domaine: $DOMAIN"
echo "🔗 Application Fly.io: $FLY_APP"
echo "📍 IP v4: $FLY_IPV4"
echo "📍 IP v6: $FLY_IPV6"

# Configurer les certificats SSL
echo ""
echo "🔒 Configuration des certificats SSL..."
export PATH="$HOME/.fly/bin:$PATH"

echo "Creating certificate for $DOMAIN..."
flyctl certs create $DOMAIN -a $FLY_APP

echo "Creating certificate for www.$DOMAIN..."
flyctl certs create www.$DOMAIN -a $FLY_APP

# Afficher la configuration DNS
echo ""
echo "📋 Configuration DNS à faire dans votre interface Gandi :"
echo "=========================================================="
echo ""
echo "🔹 ÉTAPE 1 - Enregistrement A pour le domaine principal:"
echo "   Type: A"
echo "   Nom: @"
echo "   Valeur: $FLY_IPV4"
echo "   TTL: 300"
echo ""
echo "🔹 ÉTAPE 2 - Enregistrement CNAME pour www:"
echo "   Type: CNAME" 
echo "   Nom: www"
echo "   Valeur: $FLY_DOMAIN"
echo "   TTL: 300"
echo ""
echo "🔹 ÉTAPE 3 - Enregistrement AAAA pour IPv6 (optionnel):"
echo "   Type: AAAA"
echo "   Nom: @"
echo "   Valeur: $FLY_IPV6"
echo "   TTL: 300"

# Mise à jour des ALLOWED_HOSTS
echo ""
echo "🔧 Mise à jour des ALLOWED_HOSTS dans Django..."

# Lire le fichier settings actuel
SETTINGS_FILE="app/ictgroup/settings.py"
if [ -f "$SETTINGS_FILE" ]; then
    # Sauvegarder l'original
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup"
    
    # Chercher si ALLOWED_HOSTS existe déjà
    if grep -q "ALLOWED_HOSTS" "$SETTINGS_FILE"; then
        echo "   ✅ ALLOWED_HOSTS trouvé, mise à jour..."
        # Remplacer la ligne ALLOWED_HOSTS
        sed -i "s/^ALLOWED_HOSTS = .*/ALLOWED_HOSTS = [\"$FLY_DOMAIN\", \".fly.dev\", \"$DOMAIN\", \"www.$DOMAIN\", \"localhost\", \"127.0.0.1\"]/" "$SETTINGS_FILE"
    else
        echo "   ➕ Ajout de ALLOWED_HOSTS..."
        echo "" >> "$SETTINGS_FILE"
        echo "ALLOWED_HOSTS = [\"$FLY_DOMAIN\", \".fly.dev\", \"$DOMAIN\", \"www.$DOMAIN\", \"localhost\", \"127.0.0.1\"]" >> "$SETTINGS_FILE"
    fi
    echo "   ✅ Configuration Django mise à jour"
else
    echo "   ⚠️  Fichier settings.py non trouvé dans $SETTINGS_FILE"
fi

echo ""
echo "📱 Instructions manuelles pour Gandi :"
echo "======================================"
echo ""
echo "1. 🌐 Connectez-vous à https://admin.gandi.net"
echo "2. 📂 Allez dans 'Domaines' > '$DOMAIN'"
echo "3. ⚙️  Cliquez sur 'Gérer' > 'Enregistrements DNS'"
echo "4. ➕ Ajoutez/Modifiez les enregistrements selon la configuration ci-dessus"
echo "5. 💾 Sauvegardez les modifications"
echo ""

# Redéploiement
echo "🚀 Redéploiement de l'application..."
flyctl deploy -a $FLY_APP

echo ""
echo "✅ Configuration terminée !"
echo "========================================="
echo ""
echo "🌐 Votre site sera accessible sur :"
echo "   - https://$DOMAIN"
echo "   - https://www.$DOMAIN"
echo "   - https://$FLY_DOMAIN (domaine de secours)"
echo ""
echo "⏰ La propagation DNS prend généralement 5-30 minutes"
echo ""
echo "🔍 Pour vérifier la progression :"
echo "   flyctl certs show $DOMAIN -a $FLY_APP"
echo "   nslookup $DOMAIN"
echo ""
echo "📞 En cas de problème, vérifiez :"
echo "   - Configuration DNS dans Gandi"
echo "   - Status des certificats: flyctl certs list -a $FLY_APP"
echo "   - Logs: flyctl logs -a $FLY_APP"
