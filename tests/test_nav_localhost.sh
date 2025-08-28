#!/bin/bash

# Script de test de navigation en localhost
echo "🔍 DIAGNOSTIC NAVIGATION - LOCALHOST"
echo "=================================="

echo "📡 1. Test de connectivité serveur..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/extranet/login/

echo ""
echo "🔍 2. Analyse des éléments de navigation..."
curl -s http://localhost:8000/extranet/login/ | grep -c "<header" && echo "✅ Header présent" || echo "❌ Header manquant"
curl -s http://localhost:8000/extranet/login/ | grep -c "aria-label.*Menu" && echo "✅ Menu navigation présent" || echo "❌ Menu navigation manquant"
curl -s http://localhost:8000/extranet/login/ | grep -c "mobile-menu" && echo "✅ Menu mobile présent" || echo "❌ Menu mobile manquant"
curl -s http://localhost:8000/extranet/login/ | grep -c "hamburger" && echo "✅ Bouton hamburger présent" || echo "❌ Bouton hamburger manquant"

echo ""
echo "🎨 3. Test des styles CSS..."
curl -s http://localhost:8000/extranet/login/ | grep -c "bg-gradient\|flex\|hidden" && echo "✅ Classes Tailwind détectées" || echo "❌ Classes Tailwind manquantes"

echo ""
echo "📱 4. Test structure HTML navigation..."
echo "Header tags:"
curl -s http://localhost:8000/extranet/login/ | grep -o "<header[^>]*>" | head -3

echo ""
echo "Nav tags:"  
curl -s http://localhost:8000/extranet/login/ | grep -o "<nav[^>]*>" | head -3

echo ""
echo "🔗 5. Test lien utilisateurs (sans auth)..."
curl -s -I http://localhost:8000/extranet/utilisateurs/ | grep -E "(Status|Location|HTTP)"

echo ""
echo "🏁 Diagnostic terminé"
