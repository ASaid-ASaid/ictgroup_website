#!/bin/bash

# Script de déploiement pour Fly.io
# Ce script installe Fly CLI et déploie l'application

echo "🚀 Déploiement sur Fly.io"

# Vérifier si flyctl est installé
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installation de Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

# Vérifier si l'application existe déjà
if flyctl apps list | grep -q "ictgroup-website"; then
    echo "📝 Application existante détectée, mise à jour..."
    flyctl deploy
else
    echo "🆕 Création d'une nouvelle application..."
    flyctl launch --no-deploy
    
    echo "🔧 Configuration des secrets..."
    echo "Vous devez configurer les variables d'environnement suivantes :"
    echo "- DJANGO_SECRET_KEY: Clé secrète Django"
    echo "- DATABASE_URL: URL de la base de données PostgreSQL"
    echo "- DEBUG: False pour la production"
    
    echo "Exemple de commandes :"
    echo "flyctl secrets set DJANGO_SECRET_KEY='votre-cle-secrete-tres-longue'"
    echo "flyctl secrets set DEBUG=False"
    
    # Créer une base de données PostgreSQL
    echo "🗄️ Création de la base de données PostgreSQL..."
    flyctl postgres create --name ictgroup-db --region cdg
    
    echo "🔗 Attachement de la base de données..."
    flyctl postgres attach ictgroup-db
    
    echo "🚀 Déploiement de l'application..."
    flyctl deploy
fi

echo "✅ Déploiement terminé !"
echo "🌐 Votre application est disponible sur : https://ictgroup-website.fly.dev"
