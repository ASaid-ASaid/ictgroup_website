# Guide des Heures Supplémentaires - Weekend Télétravail

## Vue d'ensemble

Le système de gestion des heures supplémentaires permet de :
- Déclarer des heures travaillées pendant les weekends en télétravail
- Gérer l'approbation par les managers et RH
- Suivre les statistiques mensuelles et annuelles
- Permettre aux validateurs de créer et approuver des demandes pour tout utilisateur

## Fonctionnalités principales

### 1. Création de demandes

**Pour les utilisateurs normaux :**
- Accès via le menu "Heures supplémentaires" → "Nouvelle demande"
- Sélection d'une date de weekend (samedi ou dimanche uniquement)
- Saisie du nombre d'heures travaillées
- Description du travail effectué
- Statut initial : "En attente"

**Pour les validateurs (Manager/RH/Admin) :**
- Formulaire étendu avec sélection d'utilisateur
- Possibilité de créer des demandes pour n'importe quel utilisateur
- Auto-approbation automatique des demandes créées

### 2. Validation et approbation

**Processus standard :**
1. Utilisateur soumet une demande → "En attente"
2. Manager valide → "En attente RH"
3. RH valide → "Approuvée"

**Processus validateur :**
- Les demandes créées par un validateur sont automatiquement approuvées
- Validation manager et RH marquées comme effectuées

### 3. Restrictions et validations

**Contraintes temporelles :**
- Seuls les weekends (samedi/dimanche) sont autorisés
- Une seule demande par utilisateur et par date

**Contraintes de rôle :**
- Utilisateurs normaux : peuvent créer des demandes pour eux-mêmes uniquement
- Managers/RH : peuvent créer et approuver des demandes pour tous
- Admins : accès total à toutes les fonctionnalités

### 4. Dashboard et statistiques

**Affichage principal :**
- Card "Heures supplémentaires ce mois" (visible uniquement si > 0)
- Intégration dans la section "Mes demandes récentes"
- Lien rapide vers la création de demande

**Données affichées :**
- Heures supplémentaires du mois en cours
- Heures supplémentaires de l'année en cours
- Historique des demandes avec statuts

### 5. Mise à jour automatique

**Signaux Django :**
- Mise à jour automatique des statistiques lors de changement de statut
- Recalcul des totaux mensuels en temps réel
- Logs détaillés pour le suivi

**Commande de maintenance :**
```bash
# Mettre à jour toutes les statistiques
python manage.py update_overtime_stats --all

# Mettre à jour pour un utilisateur spécifique
python manage.py update_overtime_stats --user username

# Mettre à jour pour une période spécifique
python manage.py update_overtime_stats --month 8 --year 2025
```

## Architecture technique

### Modèles

**OverTimeRequest :**
- `user` : Utilisateur concerné
- `work_date` : Date de travail (weekend)
- `hours` : Nombre d'heures (décimal)
- `description` : Description du travail
- `status` : pending/approved/rejected/cancelled
- `manager_validated/rh_validated` : Flags de validation

**MonthlyUserStats :**
- `overtime_hours` : Total des heures supplémentaires approuvées du mois
- Mise à jour automatique via `update_from_requests()`

### Vues et permissions

**overtime_views.py :**
- `overtime_list` : Liste avec filtres par statut et utilisateur
- `overtime_create` : Création avec formulaire adapté au rôle
- `overtime_detail/edit/delete` : CRUD complet
- Permissions basées sur les rôles utilisateur

### Templates

**Interface utilisateur :**
- `overtime_list.html` : Liste responsive avec filtres
- `overtime_form.html` : Formulaire standard utilisateur
- `overtime_admin_form.html` : Formulaire étendu validateur
- Intégration dashboard dans `home.html`

### Signaux et automatisation

**signals.py :**
- `update_stats_on_overtime_save` : Mise à jour lors de création/modification
- `update_stats_on_overtime_delete` : Mise à jour lors de suppression
- Logging complet des opérations

## Utilisation pratique

### Cas d'usage 1 : Utilisateur normal

1. Se connecter au système
2. Menu "Heures supplémentaires" → "Nouvelle demande"
3. Sélectionner un samedi ou dimanche
4. Saisir les heures et la description
5. Soumettre → Attendre l'approbation

### Cas d'usage 2 : Validateur crée pour un utilisateur

1. Se connecter en tant que Manager/RH
2. Menu "Heures supplémentaires" → "Nouvelle demande"
3. Sélectionner l'utilisateur concerné
4. Remplir les détails de la demande
5. Soumettre → Approbation automatique

### Cas d'usage 3 : Suivi et reporting

1. Dashboard : vue des heures du mois
2. Liste des demandes : filtrage et recherche
3. Commande maintenance : recalcul global
4. Logs système : suivi des modifications

## Sécurité et audit

**Contrôles d'accès :**
- Vérification des rôles à chaque action
- Isolation des données par utilisateur (sauf validateurs)
- Validation des données côté serveur et client

**Traçabilité :**
- Horodatage de toutes les actions
- Logs détaillés dans Django
- Historique des modifications de statut

## Maintenance

**Surveillance :**
- Vérifier régulièrement les logs d'erreur
- Surveiller les statistiques incohérentes
- Valider les totaux mensuels

**Commandes utiles :**
```bash
# Vérifier la cohérence des données
python manage.py update_overtime_stats --all

# Voir les logs récents
docker-compose logs web | grep overtime

# Backup des données
python manage.py dumpdata extranet.OverTimeRequest > backup_overtime.json
```

Ce système offre une gestion complète et automatisée des heures supplémentaires weekend avec un contrôle précis des permissions et une intégration native dans l'interface utilisateur existante.
