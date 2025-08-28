#!/bin/bash

echo "🔍 TEST FINAL - NAVIGATION PAGE UTILISATEURS"
echo "============================================"

echo "📡 1. Test serveur Django actif..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/extranet/login/)
echo "   Status login: $STATUS"

if [ "$STATUS" = "200" ]; then
    echo "✅ Serveur Django opérationnel"
else
    echo "❌ Serveur Django problème"
    exit 1
fi

echo ""
echo "🔍 2. Analyse template user_admin.html..."

# Compter les blocs dans le template
BLOCKS=$(grep -c "{% block" /code/app/extranet/templates/extranet/user_admin.html)
ENDBLOCKS=$(grep -c "{% endblock" /code/app/extranet/templates/extranet/user_admin.html)

echo "   Blocs trouvés: $BLOCKS"
echo "   EndBlocks trouvés: $ENDBLOCKS"

if [ "$BLOCKS" = "$ENDBLOCKS" ]; then
    echo "✅ Structure de blocs cohérente"
else
    echo "❌ Structure de blocs incohérente"
fi

echo ""
echo "🔍 3. Vérification éléments de navigation dans template..."

HEADER_COUNT=$(grep -c "<header" /code/app/extranet/templates/extranet/base.html)
NAV_COUNT=$(grep -c "<nav" /code/app/extranet/templates/extranet/base.html)
MOBILE_COUNT=$(grep -c "mobile-menu" /code/app/extranet/templates/extranet/base.html)

echo "   Headers dans base.html: $HEADER_COUNT"
echo "   Nav dans base.html: $NAV_COUNT" 
echo "   Mobile menu dans base.html: $MOBILE_COUNT"

if [ "$HEADER_COUNT" -gt 0 ] && [ "$NAV_COUNT" -gt 0 ]; then
    echo "✅ Navigation présente dans base.html"
else
    echo "❌ Navigation manquante dans base.html"
fi

echo ""
echo "🔍 4. Test template extends..."

EXTENDS=$(grep -c "{% extends" /code/app/extranet/templates/extranet/user_admin.html)
BASE_NAME=$(grep "{% extends" /code/app/extranet/templates/extranet/user_admin.html | cut -d"'" -f2)

echo "   Extends trouvé: $EXTENDS"
echo "   Template parent: $BASE_NAME"

if [ "$EXTENDS" = "1" ] && [ "$BASE_NAME" = "extranet/base.html" ]; then
    echo "✅ Template extends correctement base.html"
else
    echo "❌ Problème extends template"
fi

echo ""
echo "🎯 DIAGNOSTIC:"

if [ "$BLOCKS" = "$ENDBLOCKS" ] && [ "$HEADER_COUNT" -gt 0 ] && [ "$EXTENDS" = "1" ]; then
    echo "✅ Structure template CORRECTE"
    echo "   ➜ La navigation DEVRAIT s'afficher"
    echo "   ➜ Vérifiez votre connexion admin et videz le cache navigateur"
else
    echo "❌ Structure template INCORRECTE"
    echo "   ➜ Problèmes détectés dans la structure"
fi

echo ""
echo "💡 SOLUTION RECOMMANDÉE:"
echo "   1. Connectez-vous avec un compte admin"
echo "   2. Allez sur http://localhost:8000/extranet/utilisateurs/"
echo "   3. Videz le cache (Ctrl+F5)"
echo "   4. Sur mobile, cliquez sur le bouton ☰"

echo ""
echo "🏁 Test terminé"
