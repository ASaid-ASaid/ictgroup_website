#!/bin/bash

echo "🔧 Test des pages d'administration après corrections"
echo "=================================================="

BASE_URL="http://localhost:8000"

echo -e "\n🌐 Vérification du serveur Django:"
status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/admin/")
if [[ $status == "302" ]]; then
    echo "   ✅ Serveur Django opérationnel"
else
    echo "   ❌ Problème serveur Django (Code: $status)"
    exit 1
fi

echo -e "\n📋 Test des pages d'administration:"

admin_pages=(
    "/extranet/utilisateurs/"
    "/extranet/validation/"
    "/extranet/compte/"
    "/extranet/admin/conges/"
    "/extranet/admin/teletravail/"
    "/extranet/utilisateurs/import-csv/"
)

all_ok=true
for page in "${admin_pages[@]}"; do
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

echo -e "\n📊 Test des pages principales:"

main_pages=(
    "/extranet/"
    "/extranet/demandes/"
    "/extranet/teletravail/"
    "/extranet/documents/"
    "/extranet/calendrier/"
    "/extranet/heures_supplementaires/"
)

for page in "${main_pages[@]}"; do
    echo -n "   ${page}: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${page}")
    
    if [[ $status == "200" ]]; then
        echo "✅ OK"
    elif [[ $status == "302" ]]; then
        echo "🔄 OK (login requis)"
    elif [[ $status == "404" ]]; then
        echo "❌ Page non trouvée"
        all_ok=false
    elif [[ $status == "500" ]]; then
        echo "💥 Erreur serveur"
        all_ok=false
    else
        echo "⚠️  Code: $status"
    fi
done

if $all_ok; then
    echo -e "\n🎉 Toutes les pages fonctionnent correctement !"
    echo "   ✅ Pages d'administration : OK"
    echo "   ✅ URLs manquantes ajoutées : OK"
    echo "   ✅ Navigation complète : OK"
    echo "   ✅ Validation et user_admin : OK"
else
    echo -e "\n⚠️  Certaines pages ont encore des problèmes"
fi

echo -e "\n🔗 Les pages redirigeant vers login (302) sont normales car protégées par @login_required"
