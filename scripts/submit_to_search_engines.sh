#!/bin/bash
# Script pour soumettre le site aux moteurs de recherche et vérifier l'indexation

SITE_URL="https://ictgroup.fr"
SITEMAP_URL="https://ictgroup.fr/sitemap.xml"

echo "🚀 Soumission du site ICTGROUP aux moteurs de recherche"
echo "=================================================="

# 1. Ping Google pour notifier le sitemap
echo "📡 Notification Google du sitemap..."
curl -s "https://www.google.com/ping?sitemap=${SITEMAP_URL}" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Google notifié avec succès"
else
    echo "❌ Erreur lors de la notification Google"
fi

# 2. Ping Bing pour notifier le sitemap
echo "📡 Notification Bing du sitemap..."
curl -s "https://www.bing.com/ping?sitemap=${SITEMAP_URL}" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Bing notifié avec succès"
else
    echo "❌ Erreur lors de la notification Bing"
fi

# 3. Vérifier l'accessibilité du robots.txt
echo "🤖 Vérification du robots.txt..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}/robots.txt")
if [ "$STATUS_CODE" = "200" ]; then
    echo "✅ robots.txt accessible (Code: $STATUS_CODE)"
else
    echo "❌ robots.txt inaccessible (Code: $STATUS_CODE)"
fi

# 4. Vérifier l'accessibilité du sitemap
echo "🗺️  Vérification du sitemap.xml..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SITEMAP_URL}")
if [ "$STATUS_CODE" = "200" ]; then
    echo "✅ sitemap.xml accessible (Code: $STATUS_CODE)"
else
    echo "❌ sitemap.xml inaccessible (Code: $STATUS_CODE)"
fi

# 5. Tester la vitesse de chargement
echo "⚡ Test de vitesse de chargement..."
LOAD_TIME=$(curl -s -o /dev/null -w "%{time_total}" "${SITE_URL}")
echo "⏱️  Temps de chargement: ${LOAD_TIME}s"

# 6. Vérifier l'indexation Google actuelle
echo "🔍 Vérification de l'indexation Google..."
GOOGLE_RESULTS=$(curl -s "https://www.google.com/search?q=site:ictgroup.fr" | grep -c "ictgroup.fr" || echo "0")
echo "📊 Résultats trouvés sur Google: $GOOGLE_RESULTS"

echo ""
echo "📋 RÉSUMÉ DES ACTIONS À FAIRE MANUELLEMENT:"
echo "=========================================="
echo "1. 🔗 Aller sur https://search.google.com/search-console"
echo "2. ➕ Ajouter la propriété: ictgroup.fr"
echo "3. ✅ Vérifier la propriété (méthode DNS ou fichier HTML)"
echo "4. 📤 Soumettre le sitemap: ${SITEMAP_URL}"
echo "5. 🔄 Demander une indexation manuelle de l'URL principale"
echo ""
echo "📊 OUTILS DE VÉRIFICATION SEO:"
echo "==============================="
echo "• PageSpeed Insights: https://pagespeed.web.dev/analysis?url=${SITE_URL}"
echo "• Test de données structurées: https://search.google.com/test/rich-results?url=${SITE_URL}"
echo "• Outil d'inspection d'URL: Utiliser Google Search Console"
echo ""
echo "⏰ L'indexation peut prendre de quelques heures à plusieurs jours."
