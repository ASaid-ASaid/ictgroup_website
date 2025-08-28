# Guide de Configuration Supabase pour ICTGROUP

## 1. Configuration initiale de Supabase

### Étape 1: Créer un projet Supabase
1. Allez sur [https://supabase.com](https://supabase.com)
2. Créez un compte ou connectez-vous
3. Créez un nouveau projet :
   - Nom: `ictgroup-extranet`
   - Organisation: Votre organisation
   - Région: Choisissez la région la plus proche (ex: West EU)
   - Mot de passe de base de données: Générez un mot de passe fort

### Étape 2: Récupérer les clés d'API
1. Dans votre projet Supabase, allez dans `Settings` > `API`
2. Notez les informations suivantes :
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **anon public key**: Clé publique pour l'authentification côté client
   - **service_role secret key**: Clé secrète pour les opérations administratives

## 2. Configuration des variables d'environnement

### Pour le développement local
Créez un fichier `.env` dans le répertoire racine :

```bash
# Configuration Supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### Pour Fly.io (production)
Configurez les secrets Fly.io :

```bash
# Depuis le terminal dans le répertoire du projet
flyctl secrets set SUPABASE_URL=https://your-project-ref.supabase.co
flyctl secrets set SUPABASE_ANON_KEY=your-anon-key-here
flyctl secrets set SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

## 3. Configuration de la base de données

### Étape 1: Exécuter le script SQL
1. Dans Supabase, allez dans `SQL Editor`
2. Créez une nouvelle requête
3. Copiez le contenu du fichier `supabase_setup.sql`
4. Exécutez le script pour créer les tables

### Étape 2: Configuration du Storage
1. Allez dans `Storage` dans Supabase
2. Créez les buckets suivants :
   - `documents` (privé) : Pour les documents utilisateur
   - `avatars` (public) : Pour les avatars utilisateur

### Étape 3: Configuration de l'authentification (optionnel)
Si vous voulez utiliser l'authentification Supabase :
1. Allez dans `Authentication` > `Settings`
2. Configurez les providers souhaités (email, Google, etc.)
3. Configurez les redirections URLs

## 4. Intégration avec Django

### Services disponibles
Le service `SupabaseService` fournit les fonctionnalités suivantes :

#### Logs d'activité
```python
from extranet.supabase_service import supabase_service

# Enregistrer une activité
supabase_service.log_user_activity(
    user_id=request.user.id,
    action='login',
    details={'ip': request.META.get('REMOTE_ADDR')}
)

# Récupérer l'activité
activities = supabase_service.get_user_activity(user_id, limit=50)
```

#### Notifications
```python
# Créer une notification
supabase_service.create_notification(
    user_id=request.user.id,
    title='Nouvelle demande',
    message='Votre demande de congé a été approuvée',
    notification_type='success'
)

# Récupérer les notifications
notifications = supabase_service.get_user_notifications(user_id)
```

#### Gestion de documents
```python
# Upload un document
file_url = supabase_service.upload_document(
    bucket='documents',
    file_path=f'user_{user_id}/document.pdf',
    file_data=file_content
)

# Générer une URL signée
signed_url = supabase_service.get_document_url(
    bucket='documents',
    file_path='user_1/document.pdf'
)
```

## 5. Vues Django avec Supabase

### Dashboard avec analytics
```python
from extranet.supabase_views import dashboard_with_analytics

# URL pattern
urlpatterns = [
    path('dashboard/analytics/', dashboard_with_analytics, name='dashboard_analytics'),
]
```

### Enregistrement automatique d'activités
Ajoutez le middleware dans `settings.py` :

```python
MIDDLEWARE = [
    # ... autres middlewares
    'extranet.supabase_views.ActivityLoggingMiddleware',
]
```

## 6. Frontend JavaScript

### Enregistrer une activité depuis le frontend
```javascript
function logActivity(action, details = {}) {
    fetch('/extranet/api/log-activity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            action: action,
            details: details
        })
    });
}
```

## 7. Sécurité et bonnes pratiques

### Row Level Security (RLS)
- Les politiques RLS sont configurées automatiquement
- Chaque utilisateur ne peut accéder qu'à ses propres données
- Les clés service_role contournent RLS (à utiliser avec précaution)

### Gestion des erreurs
- Le service vérifie automatiquement la disponibilité de Supabase
- Les erreurs sont loggées mais n'interrompent pas l'application
- Mode dégradé si Supabase n'est pas disponible

### Performance
- Utilisez des index appropriés (déjà configurés dans le script SQL)
- Limitez les requêtes avec `limit`
- Mettez en cache les résultats si nécessaire

## 8. Commandes utiles

### Test de la connexion
```python
python manage.py shell
>>> from extranet.supabase_service import supabase_service
>>> print(supabase_service.is_available())
```

### Déploiement avec nouvelles dépendances
```bash
# Redéployer sur Fly.io
flyctl deploy
```

## 9. Monitoring et debug

### Vérifier les logs Supabase
1. Dans Supabase Dashboard, allez dans `Logs`
2. Filtrez par API, Auth, ou Database selon le besoin

### Debug local
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Les erreurs Supabase seront affichées dans la console
```

## 10. Migration des données existantes

Si vous avez des données existantes dans Django à migrer vers Supabase :

```python
# Script de migration personnalisé
from django.contrib.auth.models import User
from extranet.supabase_service import supabase_service

def migrate_user_activities():
    for user in User.objects.all():
        # Migrer les activités existantes
        supabase_service.log_user_activity(
            user.id,
            'account_migrated',
            {'migration_date': 'now()'}
        )
```

Cette configuration vous permet d'avoir un système d'analytics et de notifications robuste avec Supabase tout en conservant votre base de données Django principale.
