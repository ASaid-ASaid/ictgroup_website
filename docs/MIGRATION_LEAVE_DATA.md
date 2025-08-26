# Guide de Migration des Données de Congés - Ancien vers Nouveau Système

## Vue d'ensemble

Ce guide détaille la procédure complète pour migrer les données de congés de votre ancien système vers le nouveau système basé sur `UserLeaveBalance`. La migration se fait en deux étapes principales :

1. **Import des données historiques** : Importer les soldes existants (acquis, pris, report) jusqu'à fin août
2. **Migration vers période courante** : Calculer les reports et acquis pour la nouvelle période de congés

## Étape 1 : Préparation des données

### Format CSV (recommandé)
Créez un fichier CSV avec les colonnes suivantes :

```csv
username,days_acquired,days_taken,days_carry_over,site,notes
ASaid,25.0,8.0,2.5,tunisie,Manager - Report de 2024
NBenz,25.0,3.0,0.0,tunisie,Développeur
FHmai,25.0,15.0,1.0,france,Consultant - Report partiel
```

**Colonnes obligatoires :**
- `username` : Nom d'utilisateur exact dans le système
- `days_acquired` : Jours de congés acquis dans la période (ex: 25.0)
- `days_taken` : Jours de congés déjà pris (ex: 8.0)
- `days_carry_over` : Report de l'année précédente (ex: 2.5)

**Colonnes optionnelles :**
- `site` : tunisie/france (pour information)
- `notes` : Commentaires libres

### Format JSON (alternatif)
```json
[
  {
    "username": "ASaid",
    "days_acquired": 25.0,
    "days_taken": 8.0,
    "days_carry_over": 2.5,
    "site": "tunisie",
    "notes": "Manager - Report de 2024"
  }
]
```

## Étape 2 : Import des données historiques

### Commande d'import

```bash
# Test en mode simulation
python manage.py migrate_leave_data --file /path/to/data.csv --period-start 2024-06-01 --dry-run

# Import réel
python manage.py migrate_leave_data --file /path/to/data.csv --period-start 2024-06-01

# Écraser les données existantes si nécessaire
python manage.py migrate_leave_data --file /path/to/data.csv --period-start 2024-06-01 --force
```

### Mode interactif (pour petites équipes)

```bash
python manage.py migrate_leave_data --interactive --period-start 2024-06-01
```

Cette commande vous demandera de saisir les données utilisateur par utilisateur.

### Vérification de l'import

```bash
# Vérifier les données importées
docker-compose exec web python manage.py shell -c "
from extranet.models import UserLeaveBalance
from datetime import date

balances = UserLeaveBalance.objects.filter(period_start=date(2024, 6, 1))
for balance in balances[:5]:
    print(f'{balance.user.username}: {balance.days_remaining}j restants')
"
```

## Étape 3 : Migration vers la période courante

Une fois les données historiques importées, migrez vers la période courante avec calcul automatique des reports.

### Commande de migration de période

```bash
# Test en mode simulation
python manage.py migrate_to_current_period --dry-run

# Migration réelle
python manage.py migrate_to_current_period

# Spécifier la période source si différente
python manage.py migrate_to_current_period --from-period 2024-06-01

# Écraser les données de la période courante
python manage.py migrate_to_current_period --force
```

### Règles de migration automatique

**Reports :**
- Maximum 5 jours de report autorisé
- Si solde précédent > 5j → report = 5j
- Si solde précédent ≤ 5j → report = solde restant
- Si solde négatif → report = 0j

**Jours acquis :**
- Calculés automatiquement selon les règles d'acquisition
- Basés sur la date d'embauche et le site (Tunisie/France)
- Proratisés selon les mois travaillés

## Étape 4 : Vérification et validation

### Contrôles post-migration

```bash
# Vérifier les soldes utilisateurs
python manage.py shell -c "
from django.contrib.auth.models import User
from extranet.models import get_leave_balance

for user in User.objects.filter(is_active=True)[:5]:
    balance = get_leave_balance(user)
    print(f'{user.username}: {balance[\"remaining\"]}j restants')
"

# Vérifier les deux périodes
python manage.py shell -c "
from extranet.models import UserLeaveBalance
from datetime import date

print('Période 2024-2025:')
for b in UserLeaveBalance.objects.filter(period_start=date(2024,6,1))[:3]:
    print(f'  {b.user.username}: {b.days_remaining}j')

print('Période 2025-2026:')  
for b in UserLeaveBalance.objects.filter(period_start=date(2025,6,1))[:3]:
    print(f'  {b.user.username}: {b.days_remaining}j')
"
```

### Tests dashboard

1. Connectez-vous en tant qu'utilisateur
2. Vérifiez que les soldes s'affichent correctement
3. Testez la création d'une demande de congé
4. Vérifiez le calcul automatique des jours

## Étape 5 : Maintenance et corrections

### Commandes utiles

```bash
# Recalculer les jours pris pour un utilisateur
python manage.py shell -c "
from extranet.models import UserLeaveBalance
balance = UserLeaveBalance.objects.get(user__username='ASaid', period_start__year=2025)
balance.update_taken_days()
print(f'Jours pris recalculés: {balance.days_taken}')
"

# Corriger manuellement un solde
python manage.py shell -c "
from extranet.models import UserLeaveBalance
balance = UserLeaveBalance.objects.get(user__username='ASaid', period_start__year=2025)
balance.days_carry_over = 3.0
balance.save()
print('Solde corrigé')
"

# Supprimer les données de test
python manage.py shell -c "
from extranet.models import UserLeaveBalance
from datetime import date
UserLeaveBalance.objects.filter(period_start=date(2024,6,1)).delete()
print('Données de test supprimées')
"
```

### Backup et sécurité

```bash
# Backup avant migration
python manage.py dumpdata extranet.UserLeaveBalance > backup_leave_balances.json

# Restauration si nécessaire
python manage.py loaddata backup_leave_balances.json
```

## Cas d'usage complets

### Scénario 1 : Nouvelle entreprise (première migration)

```bash
# 1. Préparer le fichier CSV avec les données actuelles
# 2. Importer pour la période écoulée
python manage.py migrate_leave_data --file data.csv --period-start 2024-06-01

# 3. Migrer vers période courante
python manage.py migrate_to_current_period

# 4. Vérifier les résultats
```

### Scénario 2 : Migration en cours d'année

```bash
# Si nous sommes en septembre et que la migration démarre au 1er septembre
# 1. Importer les données jusqu'au 31 août
python manage.py migrate_leave_data --file data_august.csv --period-start 2024-06-01

# 2. Migrer immédiatement vers la période courante (2025-2026)
python manage.py migrate_to_current_period --force

# 3. Les utilisateurs utilisent désormais le nouveau système
```

### Scénario 3 : Correction après migration

```bash
# Si erreur dans les données migrées
# 1. Corriger le fichier source
# 2. Re-importer avec --force
python manage.py migrate_leave_data --file data_corrected.csv --period-start 2024-06-01 --force

# 3. Re-migrer vers période courante
python manage.py migrate_to_current_period --force
```

## Avantages du nouveau système

1. **Traçabilité complète** : Historique de toutes les périodes
2. **Calculs automatiques** : Jours pris mis à jour automatiquement
3. **Reports gérés** : Limite de 5 jours appliquée automatiquement  
4. **Multi-sites** : Règles différentes Tunisie/France
5. **Validation temps réel** : Impossible de dépasser le solde
6. **Admin interface** : Gestion facile via l'interface d'administration

## Support et dépannage

### Problèmes courants

**Erreur "User not found" :**
- Vérifier que le username existe exactement dans la base
- Créer l'utilisateur si nécessaire

**Soldes négatifs :**
- Normal si l'utilisateur a dépassé ses droits
- Corriger manuellement ou ajuster le report

**Calculs incorrects :**
- Vérifier la date d'embauche de l'utilisateur
- Recalculer avec `update_taken_days()`

Cette migration assure une transition en douceur vers le nouveau système tout en préservant l'historique et en appliquant les bonnes règles métier.
