# ⚙️ Documentation Technique

Documentation technique détaillée pour les développeurs et administrateurs système.

## 📁 Contenu

### 🚀 PERFORMANCE_OPTIMIZATION.md
Optimisation des performances
- Profiling Django
- Optimisation base de données
- Cache strategies
- Monitoring avancé

### 🗄️ SUPABASE_CONFIG.md
Configuration Supabase avancée
- Setup PostgreSQL
- Fonctions Supabase
- Storage configuration
- Real-time subscriptions

## 🏗️ Architecture Technique

### Stack Technologique
```mermaid
graph TB
    A[Frontend: Tailwind CSS + Vanilla JS] --> B[Django 5.2.5]
    B --> C[Supabase PostgreSQL]
    B --> D[Supabase Storage]
    B --> E[Redis Cache]
    F[Fly.io Platform] --> B
    G[Cloudflare CDN] --> F
```

### Composants Clés

#### Backend Django
- **Framework** : Django 5.2.5
- **Python** : 3.12+
- **WSGI** : Gunicorn
- **Database** : PostgreSQL via Supabase
- **Cache** : Redis via Supabase

#### Frontend
- **CSS** : Tailwind CSS 3.x
- **JavaScript** : ES6+ Vanilla
- **Icons** : Heroicons + Custom SVG
- **Responsive** : Mobile-first design

#### Infrastructure
- **Hosting** : Fly.io
- **CDN** : Cloudflare
- **SSL** : Let's Encrypt automatique
- **Monitoring** : Fly.io + Supabase Analytics

## 🗄️ Base de Données

### Schema Principal

#### Tables Django Standard
```sql
-- Utilisateurs et authentification
auth_user
auth_group
auth_permission
django_admin_log
django_content_type
django_sessions
```

#### Tables Extranet
```sql
-- Profils utilisateurs
extranet_userprofile
  - role (user/manager/rh/admin)
  - manager_id (hiérarchie)
  - rh_id (rattachement RH)
  - site (france/tunisie)

-- Demandes de congés
extranet_leaverequest
  - user_id, start_date, end_date
  - status, demi_jour
  - manager_validated, rh_validated

-- Demandes télétravail
extranet_teleworkrequest
  - user_id, start_date, end_date
  - status, manager_validated

-- Heures supplémentaires
extranet_overtimerequest
  - user_id, work_date, hours
  - description, status

-- Documents
extranet_document
  - title, file, category
  - permissions, target_users

-- Statistiques
extranet_monthlyuserstats
  - user_id, year, month
  - days_leave, days_telework, hours_overtime
```

### Relations Clés
```sql
-- Hiérarchie utilisateurs
UserProfile.manager_id → User.id
UserProfile.rh_id → User.id

-- Demandes utilisateur
LeaveRequest.user_id → User.id
TeleworkRequest.user_id → User.id

-- Documents et permissions
Document.target_users → ManyToMany User
```

### Index de Performance
```sql
-- Index optimisés pour requêtes fréquentes
CREATE INDEX idx_leave_user_date ON extranet_leaverequest(user_id, start_date);
CREATE INDEX idx_leave_status ON extranet_leaverequest(status);
CREATE INDEX idx_telework_user_date ON extranet_teleworkrequest(user_id, start_date);
CREATE INDEX idx_profile_manager ON extranet_userprofile(manager_id);
```

## 🔧 Configuration Système

### Variables d'Environnement

#### Production
```bash
# Django Core
SECRET_KEY=production-secret-key-very-long
DEBUG=False
ALLOWED_HOSTS=ictgroup-website.fly.dev,www.ictgroup.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Cache
REDIS_URL=redis://user:pass@host:6379/0

# Storage
SUPABASE_STORAGE_BUCKET=documents

# Email
EMAIL_HOST=smtp.mailgun.org
EMAIL_HOST_USER=postmaster@ictgroup.com
EMAIL_HOST_PASSWORD=mailgun-api-key

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Développement
```bash
# Django Core
SECRET_KEY=dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (local SQLite ou Supabase)
DATABASE_URL=sqlite:///db.sqlite3
# ou
DATABASE_URL=postgresql://postgres:password@localhost:5432/ictgroup

# Cache (optionnel en dev)
REDIS_URL=redis://localhost:6379/0

# Email (console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Configuration Django

#### Settings Structure
```python
# app/ictgroup/settings.py
from .settings_base import *

if os.getenv('FLY_APP_NAME'):
    from .settings_fly import *
else:
    from .settings_local import *
```

#### Middleware Stack
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

## 📊 Performance et Monitoring

### Métriques Clés

#### Response Times
- **Pages statiques** : < 100ms
- **Dashboard** : < 300ms
- **Rapports** : < 500ms
- **API calls** : < 200ms

#### Database Performance
```sql
-- Requêtes optimisées avec select_related
.select_related('user', 'user__profile')
.prefetch_related('user__leave_requests')

-- Cache query results
@cache_page(300)  # 5 minutes
def expensive_view(request):
    pass
```

#### Memory Usage
- **Django App** : < 512MB par instance
- **Database connections** : Pool de 20
- **Cache hit ratio** : > 85%

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
        'performance': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/performance.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'extranet.views': {
            'handlers': ['performance'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 🔒 Sécurité

### Django Security
```python
# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['https://ictgroup-website.fly.dev']

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
```

### Content Security Policy
```python
CSP_DEFAULT_SRC = ["'self'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "fonts.googleapis.com"]
CSP_FONT_SRC = ["'self'", "fonts.gstatic.com"]
CSP_SCRIPT_SRC = ["'self'"]
CSP_IMG_SRC = ["'self'", "data:", "*.supabase.co"]
```

### Rate Limiting
```python
# Django-ratelimit
@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    pass

@ratelimit(key='user', rate='100/h')
def api_view(request):
    pass
```

## 🔧 APIs et Intégrations

### Supabase Integration
```python
from supabase import create_client

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

# Real-time subscriptions
def handle_leave_update(payload):
    # Notify managers of new leave requests
    pass

supabase.table('extranet_leaverequest').on('INSERT', handle_leave_update).subscribe()
```

### Custom Management Commands
```python
# app/extranet/management/commands/sync_stats.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Synchronize monthly stats
        pass

# Usage
python manage.py sync_stats --month=2025-08
```

### Email Notifications
```python
from django.core.mail import send_mail
from django.template.loader import render_to_string

def notify_manager_new_leave(leave_request):
    context = {'leave': leave_request}
    html_message = render_to_string('emails/leave_request.html', context)
    
    send_mail(
        subject=f'Nouvelle demande de congé - {leave_request.user.get_full_name()}',
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[leave_request.user.profile.manager.email],
    )
```

## 🧪 Tests Techniques

### Test Database
```python
# settings_test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

### Performance Testing
```python
from django.test import TransactionTestCase
from django.test.utils import override_settings
import time

class PerformanceTest(TransactionTestCase):
    def test_dashboard_performance(self):
        start_time = time.time()
        response = self.client.get('/extranet/')
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 0.5)  # < 500ms
        self.assertEqual(response.status_code, 200)
```

### Load Testing
```bash
# Artillery.js config
npm install -g artillery
artillery run tests/load/basic_load.yml
```

## 📈 Optimisations Avancées

### Database Query Optimization
```python
# Optimized queries with annotations
users_with_stats = User.objects.select_related('profile').annotate(
    total_leaves=Count('leave_requests'),
    pending_leaves=Count('leave_requests', filter=Q(leave_requests__status='pending')),
    leave_days_used=Sum('leave_requests__get_nb_days', filter=Q(leave_requests__status='approved'))
).prefetch_related('leave_requests__user')
```

### Caching Strategies
```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page

# View caching
@cache_page(60 * 15)  # 15 minutes
def monthly_report(request):
    pass

# Template fragment caching
{% load cache %}
{% cache 300 user_stats user.id %}
    <!-- Expensive user stats -->
{% endcache %}

# Manual caching
def get_user_leave_balance(user_id):
    cache_key = f'leave_balance_{user_id}'
    balance = cache.get(cache_key)
    if balance is None:
        balance = calculate_leave_balance(user_id)
        cache.set(cache_key, balance, 3600)  # 1 hour
    return balance
```

### Background Tasks
```python
# Using Celery (future enhancement)
from celery import shared_task

@shared_task
def process_monthly_stats():
    # Heavy computation in background
    pass

# Scheduled with Celery Beat
CELERY_BEAT_SCHEDULE = {
    'monthly-stats': {
        'task': 'extranet.tasks.process_monthly_stats',
        'schedule': crontab(day_of_month=1, hour=2, minute=0),
    },
}
```
