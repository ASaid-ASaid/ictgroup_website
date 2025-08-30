# 🏢 Guide Utilisateur - Intranet ICTGROUP

## Vue d'ensemble

L'intranet ICTGROUP est votre espace de travail administratif dédié à la gestion financière et opérationnelle de l'entreprise. Accessible uniquement aux administrateurs, il centralise tous les outils nécessaires à la gestion quotidienne.

## Accès à l'Intranet

### Conditions d'Accès
- **Statut** : Superutilisateur Django ou profil administrateur
- **URL** : `https://ictgroup.fr/intranet/` (production) ou `http://localhost:8000/intranet/` (développement)
- **Authentification** : Utilisez vos identifiants Django habituels

### Sécurité
- **Accès restreint** : Réservé aux administrateurs uniquement
- **Logs d'activité** : Toutes vos actions sont tracées
- **Permissions granulaires** : Contrôle d'accès par fonctionnalité

## 🏠 Tableau de Bord

### Métriques Clés
Le tableau de bord affiche en temps réel :
- **Nombre total de factures**
- **Chiffre d'affaires** (factures payées)
- **Factures en attente** de paiement
- **Bons de commande** en cours
- **Transactions récentes** (5 dernières)

### Navigation Rapide
- **Créer une facture** : Bouton direct vers le formulaire
- **Enregistrer une transaction** : Accès rapide à la trésorerie
- **Uploader un document** : Ajout de pièce jointe
- **Voir les bons de commande** : Liste des achats en cours

## 📄 Gestion des Factures

### Créer une Nouvelle Facture

#### Étape 1 : Informations Client
```
Numéro de facture : Généré automatiquement (FACT-2025-001)
Nom du client    : Société ABC
Adresse          : 123 Rue de la Paix, 75001 Paris
Email            : contact@societe-abc.com
Téléphone        : +33 1 23 45 67 89
```

#### Étape 2 : Détails de Facturation
```
Date d'émission  : 15/08/2025 (automatique)
Date d'échéance  : 15/09/2025 (30 jours par défaut)
Taux de TVA      : 20% (configurable)
```

#### Étape 3 : Lignes de Facture
Ajoutez les prestations/produits :

| Description | Quantité | Prix Unit. HT | Total HT |
|-------------|----------|---------------|----------|
| Développement web | 10 | 500€ | 5 000€ |
| Formation équipe | 2 | 800€ | 1 600€ |
| **Sous-total** | | | **6 600€** |

#### Étape 4 : Calculs Automatiques
```
Sous-total HT    : 6 600€
TVA (20%)        : 1 320€
Total TTC        : 7 920€
```

### Statuts des Factures

| Statut | Description | Actions Possibles |
|--------|-------------|-------------------|
| **Brouillon** | En cours d'édition | Modifier, Supprimer |
| **Envoyée** | Transmise au client | Modifier statut |
| **Payée** | Réglée par le client | Archiver |
| **En retard** | Échéance dépassée | Relancer client |
| **Annulée** | Facture annulée | Archiver |

### Recherche et Filtrage
- **Par numéro** : Recherche exacte
- **Par client** : Recherche partielle
- **Par statut** : Filtre par état
- **Par période** : Date d'émission ou d'échéance

## 💰 Gestion de la Trésorerie

### Enregistrer une Transaction

#### Types de Transactions

##### Recettes (Entrées)
```
Type      : Recette
Catégorie : Ventes / Services / Autres
Montant   : 7 920€
Description : Facture FACT-2025-001 - Société ABC
Référence : FACT-2025-001
```

##### Dépenses (Sorties)
```
Type      : Dépense
Catégorie : Fournitures / Loyer / Salaires / Charges
Montant   : 1 500€
Description : Achat matériel informatique
Référence : BC-2025-001
```

##### Virements (Transferts)
```
Type      : Virement
Montant   : 5 000€
Description : Transfert vers compte épargne
Compte source : Compte courant
Compte destination : Livret A
```

### Suivi des Soldes
- **Solde actuel** : Calcul automatique en temps réel
- **Historique** : Toutes les transactions tracées
- **Catégorisation** : Analyse par type de dépense/recette

## 📦 Gestion des Bons de Commande

### Créer un Bon de Commande

#### Informations Fournisseur
```
Numéro BC       : Généré automatiquement (BC-2025-001)
Nom fournisseur : Tech Solutions SARL
Adresse         : 456 Avenue des Technologies, 69000 Lyon
Email           : contact@tech-solutions.fr
Téléphone       : +33 4 56 78 90 12
```

#### Détails de Commande
```
Date de commande         : 15/08/2025
Date livraison prévue    : 30/08/2025
Date livraison effective : (rempli après réception)
```

#### Lignes de Commande
| Description | Quantité | Prix Unit. | Total |
|-------------|----------|------------|-------|
| Ordinateurs portables | 5 | 800€ | 4 000€ |
| Écrans 27" | 5 | 300€ | 1 500€ |
| **Total** | | | **5 500€** |

### Suivi des Commandes

| Statut | Description | Actions |
|--------|-------------|---------|
| **Brouillon** | En préparation | Modifier, Supprimer |
| **Envoyé** | Transmis fournisseur | Modifier statut |
| **Approuvé** | Validé en interne | Attendre livraison |
| **Reçu** | Marchandises livrées | Clôturer |
| **Annulé** | Commande annulée | Archiver |

## 📎 Gestion des Pièces Jointes

### Types de Documents
- **Factures** : Factures clients et fournisseurs
- **Reçus** : Justificatifs de paiement
- **Contrats** : Documents contractuels
- **Devis** : Propositions commerciales
- **Autres** : Documents divers

### Upload de Documents
1. **Sélectionner le fichier** : Formats acceptés (PDF, DOC, XLS, JPG, PNG)
2. **Choisir le type** : Catégorie du document
3. **Ajouter un titre** : Description courte
4. **Lier à une facture/BC** : Association optionnelle
5. **Téléverser** : Stockage sécurisé

### Organisation
- **Tri par date** : Documents les plus récents en premier
- **Filtrage par type** : Recherche par catégorie
- **Association** : Liens vers factures/commandes liées
- **Téléchargement** : Accès sécurisé aux fichiers

## 📊 Rapports et Analyses

### Tableaux de Bord
- **Chiffre d'affaires** : Évolution mensuelle
- **Trésorerie** : Solde et flux de trésorerie
- **Factures** : Statuts et délais de paiement
- **Commandes** : Suivi des achats fournisseurs

### Exports de Données
- **Format Excel** : Tableaux complets
- **Format PDF** : Rapports formatés
- **Périodes personnalisables** : Filtres par dates

## 🔒 Sécurité et Conformité

### Protection des Données
- **Chiffrement** : Données sensibles cryptées
- **Sauvegarde** : Sauvegarde automatique quotidienne
- **Accès contrôlé** : Permissions par utilisateur
- **Logs d'audit** : Traçabilité complète

### Conformité RGPD
- **Consentement** : Gestion des données clients
- **Droit d'accès** : Consultation des données
- **Droit de rectification** : Modification des données
- **Droit à l'effacement** : Suppression des données

## 📞 Support et Assistance

### Formation
- **Documentation complète** : Guides détaillés disponibles
- **Vidéos tutoriels** : Démonstrations pas à pas
- **Support technique** : Équipe disponible

### Contacts
- **Support technique** : support@ictgroup.com
- **Urgences** : +33 1 23 45 67 89
- **Documentation** : `/docs/user-guide/`

## 🔧 Dépannage

### Problèmes Courants

#### "Accès refusé"
**Cause** : Permissions insuffisantes
**Solution** : Vérifier votre statut administrateur

#### "Erreur de calcul"
**Cause** : Données manquantes ou invalides
**Solution** : Vérifier tous les champs obligatoires

#### "Upload échoué"
**Cause** : Fichier trop volumineux ou format invalide
**Solution** : Respecter les limites (10MB max, formats autorisés)

#### "Facture introuvable"
**Cause** : Erreur de numéro ou de recherche
**Solution** : Utiliser les filtres de recherche avancés

## 📈 Évolutions à Venir

### Fonctionnalités Planifiées
- **Interface mobile** : Application responsive complète
- **Notifications automatiques** : Alertes par email
- **Intégration comptable** : Synchronisation avec logiciels comptables
- **Signatures électroniques** : Validation dématérialisée
- **IA prédictive** : Analyse des tendances financières

### Améliorations Continues
- **Performance** : Optimisation des temps de chargement
- **UX/UI** : Interface utilisateur améliorée
- **Automatisation** : Workflows automatisés
- **Analytics** : Tableaux de bord avancés

---

*Guide utilisateur - Intranet ICTGROUP | Version 1.0 | Août 2025*
