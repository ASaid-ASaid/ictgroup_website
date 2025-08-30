# Intranet ICTGROUP

## Vue d'ensemble

L'intranet ICTGROUP est une plateforme administrative réservée aux administrateurs pour la gestion des aspects financiers et opérationnels de l'entreprise.

## Fonctionnalités

### 📄 Gestion des Factures
- Création et gestion des factures clients
- Calcul automatique de la TVA
- Suivi des statuts (Brouillon, Envoyée, Payée, En retard, Annulée)
- Génération de numéros de facture uniques

### 💰 Gestion de la Trésorerie
- Enregistrement des recettes et dépenses
- Catégorisation des transactions
- Suivi des virements entre comptes
- Calcul automatique des soldes

### 📦 Gestion des Bons de Commande
- Création de bons de commande fournisseurs
- Suivi des statuts de livraison
- Gestion des délais de livraison
- Calcul automatique des totaux

### 📎 Gestion des Pièces Jointes
- Téléchargement de documents (factures, reçus, contrats, devis)
- Organisation par type de document
- Association avec les factures et bons de commande

## Accès

L'intranet est accessible uniquement aux utilisateurs ayant les droits d'administrateur :
- Superutilisateurs Django (`is_superuser=True`)
- Utilisateurs avec le rôle 'admin' dans leur profil

## URLs

- `/intranet/` - Tableau de bord principal
- `/intranet/invoices/` - Gestion des factures
- `/intranet/treasury/` - Gestion de la trésorerie
- `/intranet/purchase-orders/` - Gestion des bons de commande
- `/intranet/attachments/` - Gestion des pièces jointes

## Modèles de données

### Invoice (Facture)
- Informations client
- Montants HT/TVA/TTC
- Statuts et dates
- Lignes de facture détaillées

### Treasury (Trésorerie)
- Transactions recettes/dépenses
- Catégorisation
- Références et comptes

### PurchaseOrder (Bon de commande)
- Informations fournisseur
- Articles commandés
- Statuts de livraison

### Attachment (Pièce jointe)
- Documents associés
- Types de fichiers
- Liaisons avec factures/commandes

## Sécurité

- Authentification requise
- Autorisation basée sur les rôles
- Logs d'audit sur toutes les actions
- Protection CSRF sur tous les formulaires

## Technologies utilisées

- Django 5.2
- PostgreSQL (base de données)
- HTML5/CSS3 avec Tailwind CSS
- JavaScript pour l'interactivité
- Interface d'administration Django

## Développement

### Installation
```bash
# Créer l'application
python manage.py startapp intranet

# Ajouter à INSTALLED_APPS
# intranet dans settings.py

# Créer les migrations
python manage.py makemigrations intranet

# Appliquer les migrations
python manage.py migrate
```

### Tests
```bash
# Exécuter les tests de l'intranet
python manage.py test intranet
```

## Maintenance

- Sauvegarde régulière de la base de données
- Archivage des anciens documents
- Mise à jour des statuts automatiquement
- Monitoring des performances
