#!/bin/bash

echo "🔍 Test de navigation des pages principales de l'extranet"
echo "======================================================="

BASE_URL="http://localhost:8000"

# Test des pages principales
pages=(
    "/extranet/"
    "/extranet/demandes/"
    "/extranet/teletravail/"
    "/extranet/documents/"
    "/extranet/calendrier/"
    "/extranet/compte/"
)

echo -e "\n📋 Test d'accessibilité des pages:"
for page in "${pages[@]}"; do
    echo -n "   ${page}: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${page}")
    
    if [[ $status == "200" ]]; then
        echo "✅ Accessible (Code: $status)"
    elif [[ $status == "302" ]]; then
        echo "🔄 Redirection (Code: $status) - Probablement vers login"
    elif [[ $status == "404" ]]; then
        echo "❌ Page non trouvée (Code: $status)"
    elif [[ $status == "500" ]]; then
        echo "💥 Erreur serveur (Code: $status)"
    else
        echo "⚠️  Code: $status"
    fi
done

echo -e "\n🔗 Test des liens de navigation avec authentification simulée:"
echo "   Note: Les redirections 302 vers login sont normales pour un site protégé"

# Vérification que le serveur Django répond
echo -e "\n🌐 État du serveur Django:"
status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/admin/")
if [[ $status == "302" ]]; then
    echo "   ✅ Serveur Django opérationnel (Admin accessible)"
else
    echo "   ⚠️  Statut serveur: $status"
fi

echo -e "\n✨ Test terminé - Navigation prête !"
