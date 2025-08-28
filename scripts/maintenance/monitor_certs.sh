#!/bin/bash
# monitor_certs.sh - Surveillance des certificats SSL

echo "🔍 Surveillance des certificats SSL pour ictgroup.fr"
echo "=================================================="

export PATH="$HOME/.fly/bin:$PATH"

while true; do
    echo ""
    echo "⏰ $(date '+%H:%M:%S') - Vérification..."
    
    # Vérifier les certificats
    CERTS_OUTPUT=$(flyctl certs list -a ictgroup-website 2>/dev/null)
    
    if echo "$CERTS_OUTPUT" | grep -q "Ready"; then
        echo "🎉 CERTIFICATS PRÊTS !"
        echo "$CERTS_OUTPUT"
        echo ""
        echo "✅ Votre site est maintenant accessible en HTTPS :"
        echo "   🌐 https://ictgroup.fr"
        echo "   🌐 https://www.ictgroup.fr"
        break
    else
        echo "⏳ Certificats en cours de validation..."
        echo "$CERTS_OUTPUT"
    fi
    
    # Tester la résolution DNS
    if ping -c 1 ictgroup.fr > /dev/null 2>&1; then
        echo "✅ DNS ictgroup.fr : OK"
    else
        echo "❌ DNS ictgroup.fr : Problème"
    fi
    
    if ping -c 1 www.ictgroup.fr > /dev/null 2>&1; then
        echo "✅ DNS www.ictgroup.fr : OK"
    else
        echo "⏳ DNS www.ictgroup.fr : En attente"
    fi
    
    echo "⏳ Nouvelle vérification dans 2 minutes..."
    sleep 120
done

echo ""
echo "🎯 Configuration terminée avec succès !"
echo "📱 Vous pouvez maintenant accéder à votre site en HTTPS"
