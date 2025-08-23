# Dossier de Sauvegardes

Ce dossier contient les sauvegardes automatiques du projet.

## Types de sauvegardes

### Base de données
- **Format**: `db_YYYYMMDD_HHMMSS.sql`
- **Commande**: `./manage.sh backup:db`
- **Contenu**: Dump PostgreSQL complet

### Fichiers média
- **Format**: `media_YYYYMMDD_HHMMSS.tar.gz`
- **Commande**: `./manage.sh backup:files`
- **Contenu**: Archive des fichiers uploadés

## Rétention
- Conserver les sauvegardes quotidiennes pendant 30 jours
- Conserver les sauvegardes hebdomadaires pendant 3 mois
- Conserver les sauvegardes mensuelles pendant 1 an

## Restauration

### Base de données
```bash
# Restaurer une sauvegarde
docker exec -i ictgroup-db psql -U ictgroup -d ictgroup_db < backups/db_20240101_120000.sql
```

### Fichiers média
```bash
# Restaurer les fichiers
tar -xzf backups/media_20240101_120000.tar.gz
```
