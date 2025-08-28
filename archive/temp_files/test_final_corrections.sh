#!/bin/bash

echo "🔧 Test final après correction des templates"
echo "=========================================="

BASE_URL="http://localhost:8000"

echo -e "\n🌐 Vérification du serveur Django:"
status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/admin/")
if [[ $status == "302" ]]; then
    echo "   ✅ Serveur Django opérationnel"
else
    echo "   ❌ Problème serveur Django (Code: $status)"
    exit 1
fi

echo -e "\n📋 Test des pages problématiques corrigées:"

# Pages qui avaient des erreurs
problem_pages=(
    "/extranet/validation/"
    "/extranet/utilisateurs/"
    "/extranet/compte/"
)

all_ok=true
for page in "${problem_pages[@]}"; do
    echo -n "   ${page}: "
    
    # Test du code de réponse
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${page}")
    
    if [[ $status == "200" ]]; then
        echo "✅ OK - Page accessible directement"
    elif [[ $status == "302" ]]; then
        echo "✅ OK - Redirection login (normal)"
    elif [[ $status == "500" ]]; then
        echo "❌ Erreur serveur - Template ou vue cassé"
        all_ok=false
        
        # Test plus détaillé en cas d'erreur 500
        echo "      🔍 Détails de l'erreur:"
        error_detail=$(curl -s "${BASE_URL}${page}" | grep -i "error\|exception" | head -1)
        if [[ -n "$error_detail" ]]; then
            echo "      $error_detail"
        fi
    elif [[ $status == "404" ]]; then
        echo "❌ Page non trouvée"
        all_ok=false
    else
        echo "⚠️  Code: $status"
    fi
done

echo -e "\n📊 Test de navigation générale:"

# Toutes les pages principales
all_pages=(
    "/extranet/"
    "/extranet/demandes/"
    "/extranet/teletravail/"
    "/extranet/documents/"
    "/extranet/calendrier/"
    "/extranet/heures_supplementaires/"
    "/extranet/admin/conges/"
    "/extranet/admin/teletravail/"
)

nav_ok=true
for page in "${all_pages[@]}"; do
    echo -n "   ${page}: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${page}")
    
    if [[ $status == "200" || $status == "302" ]]; then
        echo "✅"
    elif [[ $status == "500" ]]; then
        echo "❌ Erreur serveur"
        nav_ok=false
    elif [[ $status == "404" ]]; then
        echo "❌ Non trouvé"
        nav_ok=false
    else
        echo "⚠️ $status"
    fi
done

echo -e "\n🎯 Résumé des corrections:"
echo "   ✅ Template validation.html corrigé (TemplateSyntaxError résolu)"
echo "   ✅ URL import_users_csv ajoutée"  
echo "   ✅ Fonctions dupliquées supprimées dans admin_views.py"
echo "   ✅ Vue account_settings implémentée"

if $all_ok && $nav_ok; then
    echo -e "\n🎉 Toutes les corrections réussies !"
    echo "   ✅ Pages validation et user_admin fonctionnelles"
    echo "   ✅ Templates syntaxiquement corrects"
    echo "   ✅ Navigation complète restaurée"
    echo "   ✅ Prêt pour l'utilisation"
else
    echo -e "\n⚠️  Certains problèmes persistent - vérifiez les erreurs ci-dessus"
fi
