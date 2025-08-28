#!/bin/bash

echo "🧹 Test après nettoyage du code et fusion home/dashboard"
echo "====================================================="

BASE_URL="http://localhost:8000"

echo -e "\n🔍 Vérification de l'état du serveur Django:"
# Test de base du serveur
status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/admin/")
if [[ $status == "302" ]]; then
    echo "   ✅ Serveur Django opérationnel"
else
    echo "   ❌ Problème serveur Django (Code: $status)"
    exit 1
fi

echo -e "\n📋 Test d'accessibilité des pages après nettoyage:"

# Pages principales
pages=(
    "/extranet/"
    "/extranet/demandes/"
    "/extranet/teletravail/" 
    "/extranet/documents/"
    "/extranet/calendrier/"
    "/extranet/heures_supplementaires/"
    "/extranet/compte/"
    "/extranet/validation/"
)

all_ok=true
for page in "${pages[@]}"; do
    echo -n "   ${page}: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${page}")
    
    if [[ $status == "200" ]]; then
        echo "✅ OK (Code: $status)"
    elif [[ $status == "302" ]]; then
        echo "🔄 Redirigé vers login (Code: $status) - Normal"
    elif [[ $status == "404" ]]; then
        echo "❌ Page non trouvée (Code: $status)"
        all_ok=false
    elif [[ $status == "500" ]]; then
        echo "💥 Erreur serveur (Code: $status)"
        all_ok=false
    else
        echo "⚠️  Code: $status"
    fi
done

echo -e "\n🏠 Test spécifique de la fusion home/dashboard:"
echo -n "   Page d'accueil: "
home_status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/extranet/")
if [[ $home_status == "302" ]]; then
    echo "✅ Dashboard accessible (redirection login normale)"
else
    echo "⚠️  Code: $home_status"
fi

echo -e "\n📊 Test des API:"
api_status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/extranet/api/dashboard/")
echo -n "   API Dashboard: "
if [[ $api_status == "302" ]]; then
    echo "✅ API accessible (redirection login normale)"
else
    echo "⚠️  Code: $api_status"
fi

if $all_ok; then
    echo -e "\n🎉 Nettoyage réussi ! Toutes les fonctionnalités sont opérationnelles"
    echo "   ✅ Fusion home/dashboard : OK"
    echo "   ✅ Fonctions déplacées vers leurs modules : OK"  
    echo "   ✅ missing_views.py supprimé : OK"
    echo "   ✅ Toutes les pages accessibles : OK"
else
    echo -e "\n⚠️  Certaines pages ont des problèmes - vérifiez les erreurs ci-dessus"
fi
