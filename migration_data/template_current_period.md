# Modèle CSV pour Migration État au 31 Août 2025

## Contexte :
Ces données représentent l'état réel des congés de chaque utilisateur au **31 août 2025**, dans la période courante (juin 2025 - mai 2026).

## Format des colonnes :
- username : Nom d'utilisateur exact dans le système
- days_acquired : Jours acquis depuis juin 2025 jusqu'à fin août (ex: 2.5 pour ASaid)
- days_taken : Jours pris entre juin et août 2025 (ex: 8 pour ASaid)  
- days_carry_over : Report de la période précédente (ex: 20 pour ASaid)
- site : tunisie ou france
- notes : Commentaires libres

## Exemples avec vraies données au 31 août :

```csv
username,days_acquired,days_taken,days_carry_over,site,notes
ASaid,2.5,8.0,20.0,france,État au 31 août - Acquis 2.5j depuis juin
FHmai,1.8,3.0,0.0,tunisie,État au 31 août - Acquis 1.8j depuis juin
```

## Calcul automatique :
- **Restant = Acquis + Report - Pris**
- ASaid : 2.5 + 20.0 - 8.0 = 14.5j restants
- FHmai : 1.8 + 0.0 - 3.0 = -1.2j restants (déficit normal)

## Instructions d'import :

1. Complétez le fichier CSV avec vos données réelles
2. Importez avec la commande :
   ```bash
   python manage.py migrate_leave_data --file your_data.csv --period-start 2025-06-01 --force
   ```

## Notes importantes :
- Les soldes négatifs sont autorisés et normaux (utilisateur en avance sur ses droits)
- Le système calculera automatiquement les futurs acquis selon l'ancienneté
- Les rapports sont illimités car il s'agit de la vraie situation à fin août
