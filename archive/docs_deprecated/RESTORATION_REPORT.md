# Restauration de l'état avant la demande de base de développement

## Fichiers supprimés
- `docker-compose.dev.yml` - Configuration Docker pour l'environnement de développement PostgreSQL
- `app/init_dev_db.py` - Script d'initialisation de la base de développement
- `app/ictgroup/env_config.py` - Configuration multi-environnement 
- `scripts/set_env.sh` - Script de changement d'environnement
- `scripts/dev_start.sh` - Script de démarrage de l'environnement de développement
- `scripts/reset_dev_db.sh` - Script de reset de la base de développement

## Fichiers restaurés
- `app/supabase_config.py` - Restauré à la configuration originale sans gestion d'environnement
- `app/extranet/signals.py` - Restauré sans protection d'environnement pour l'accrual automatique
- `app/ictgroup/settings.py` - Restauré à la configuration originale avec SQLite par défaut

## Migrations
- Migrations problématiques sauvegardées dans `app/extranet/migrations_backup/`
- Nouvelles migrations propres créées dans `app/extranet/migrations/`
- Base SQLite recréée proprement

## État actuel
- L'application est configurée pour utiliser Supabase PostgreSQL (comme avant)
- Migrations originales restaurées
- Configuration `.env` requise avec DATABASE_URL vers Supabase
- Template créé dans `.env.supabase.template` pour vous guider

## Action requise
Vous devez configurer votre fichier `.env` avec vos vraies credentials Supabase :
```
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Notes
- L'accrual automatique fonctionne maintenant normalement (plus de protection d'environnement)
- Les formulaires conservent leurs validations détaillées avec emojis
- Le système de priorité (congé > télétravail) est toujours actif
- Vous travaillez maintenant directement avec vos données de production Supabase
