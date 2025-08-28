# 🧪 Tests

Suite de tests complète pour ICTGROUP Website organisée par type et complexité.

## 📁 Structure

```
tests/
├── unit/              # Tests unitaires - rapides, isolés
├── integration/       # Tests d'intégration - interaction composants
├── performance/       # Tests de performance - métriques temps/mémoire
├── functional/        # Tests fonctionnels - parcours utilisateur
├── __init__.py        # Configuration base tests
└── run_all_tests.py   # Runner principal
```

## 🚀 Exécution Rapide

```bash
# Tous les tests
./manage.sh test

# Par catégorie
./manage.sh test:unit          # Tests unitaires uniquement
./manage.sh test:integration   # Tests d'intégration
./manage.sh test:performance   # Tests de performance
./manage.sh test:functional    # Tests fonctionnels

# Avec couverture
./manage.sh test:coverage

# Tests spécifiques
python manage.py test tests.unit.test_models
python manage.py test tests.integration.test_views::LeaveViewTest
```

## 🎯 Types de Tests

### 🔬 Tests Unitaires (`unit/`)
Tests rapides et isolés des composants individuels.

**Contenu :**
- `test_models.py` - Models Django
- `test_forms.py` - Formulaires et validation
- `test_utils.py` - Fonctions utilitaires
- `test_calculations.py` - Logique métier

**Objectifs :**
- Couverture > 90%
- Exécution < 30 secondes
- Aucune dépendance externe

**Exemple :**
```python
# tests/unit/test_models.py
from django.test import TestCase
from extranet.models import LeaveRequest

class LeaveRequestModelTest(TestCase):
    def test_get_nb_days_full_day(self):
        """Test calcul jours complets"""
        leave = LeaveRequest(
            start_date=date(2025, 8, 28),
            end_date=date(2025, 8, 30),
            demi_jour='full'
        )
        self.assertEqual(leave.get_nb_days, 3)
    
    def test_get_nb_days_half_day(self):
        """Test calcul demi-journées"""
        leave = LeaveRequest(demi_jour='am')
        self.assertEqual(leave.get_nb_days, 0.5)
```

### 🔗 Tests d'Intégration (`integration/`)
Tests des interactions entre composants.

**Contenu :**
- `test_views.py` - Vues Django et responses
- `test_auth.py` - Authentification et permissions
- `test_api.py` - APIs et endpoints
- `test_workflows.py` - Workflows complets

**Objectifs :**
- Tests des parcours utilisateur
- Validation des permissions
- Intégration base de données

**Exemple :**
```python
# tests/integration/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class LeaveViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
    
    def test_leave_request_view_requires_login(self):
        """Test que la vue demande l'authentification"""
        response = self.client.get('/extranet/congés/demande/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_leave_request_submission(self):
        """Test soumission demande de congé"""
        self.client.login(username='test', password='pass')
        response = self.client.post('/extranet/congés/demande/', {
            'start_date': '2025-09-01',
            'end_date': '2025-09-03',
            'reason': 'Vacances d\'été'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
```

### ⚡ Tests de Performance (`performance/`)
Tests des métriques de performance et optimisation.

**Contenu :**
- `performance_tests.py` - Métriques temps de réponse
- `test_database_queries.py` - Optimisation requêtes DB
- `test_memory_usage.py` - Utilisation mémoire
- `test_load.py` - Tests de charge

**Objectifs :**
- Temps de réponse < seuils définis
- Nombre de requêtes DB optimisé
- Utilisation mémoire contrôlée

**Exemple :**
```python
# tests/performance/performance_tests.py
import time
from django.test import TestCase
from django.test.utils import override_settings

class PerformanceTest(TestCase):
    def test_dashboard_response_time(self):
        """Test temps de réponse dashboard < 500ms"""
        self.client.login(username='test', password='pass')
        
        start_time = time.time()
        response = self.client.get('/extranet/')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 0.5, f"Dashboard trop lent: {response_time}s")
        self.assertEqual(response.status_code, 200)
    
    def test_database_queries_count(self):
        """Test nombre de requêtes DB optimisé"""
        with self.assertNumQueries(5):  # Max 5 queries expected
            response = self.client.get('/extranet/congés/')
            self.assertEqual(response.status_code, 200)
```

### 🎭 Tests Fonctionnels (`functional/`)
Tests des parcours utilisateur complets.

**Contenu :**
- `test_user_journey.py` - Parcours utilisateur standard
- `test_manager_workflow.py` - Workflow manager
- `test_rh_workflow.py` - Workflow RH
- `test_admin_features.py` - Fonctionnalités admin

**Objectifs :**
- Validation expérience utilisateur
- Tests end-to-end
- Scenarios réels

**Exemple :**
```python
# tests/functional/test_user_journey.py
from django.test import TestCase
from django.contrib.auth.models import User
from extranet.models import LeaveRequest

class UserJourneyTest(TestCase):
    def test_complete_leave_request_workflow(self):
        """Test workflow complet demande de congé"""
        # 1. Création utilisateur et manager
        user = User.objects.create_user('employee', 'emp@test.com', 'pass')
        manager = User.objects.create_user('manager', 'mgr@test.com', 'pass')
        
        # 2. Login utilisateur et demande congé
        self.client.login(username='employee', password='pass')
        response = self.client.post('/extranet/congés/demande/', {
            'start_date': '2025-09-01',
            'end_date': '2025-09-03',
            'reason': 'Vacances'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. Vérification création demande
        leave = LeaveRequest.objects.get(user=user)
        self.assertEqual(leave.status, 'pending')
        
        # 4. Login manager et validation
        self.client.login(username='manager', password='pass')
        response = self.client.post('/extranet/validation/', {
            'action': 'manager_approve',
            'leave_id': leave.id
        })
        
        # 5. Vérification validation
        leave.refresh_from_db()
        self.assertTrue(leave.manager_validated)
```

## 📊 Configuration Tests

### Base de Données Test
```python
# tests/__init__.py
from django.test import override_settings
import os

# Force SQLite en mémoire pour les tests
@override_settings(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)
class BaseTestCase:
    pass
```

### Fixtures et Données Test
```python
# tests/fixtures.py
from django.contrib.auth.models import User
from extranet.models import UserProfile

class TestDataMixin:
    def create_test_user(self, username='testuser', role='user'):
        user = User.objects.create_user(
            username=username,
            email=f'{username}@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=user, role=role)
        return user
    
    def create_test_manager(self):
        return self.create_test_user('manager', 'manager')
    
    def create_test_leave_request(self, user, status='pending'):
        return LeaveRequest.objects.create(
            user=user,
            start_date='2025-09-01',
            end_date='2025-09-03',
            status=status
        )
```

### Mocks et Stubs
```python
# tests/mocks.py
from unittest.mock import Mock, patch

class SupabaseMock:
    def __init__(self):
        self.table = Mock()
        self.storage = Mock()
    
    def table(self, name):
        return Mock()

# Usage dans tests
@patch('extranet.supabase_service.supabase', SupabaseMock())
def test_with_supabase_mock(self):
    pass
```

## 🚀 Exécution et CI/CD

### Configuration PyTest (optionnel)
```ini
# pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = ictgroup.settings_test
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    functional: Functional tests
```

### Coverage Configuration
```ini
# .coveragerc
[run]
source = app/
omit = 
    */migrations/*
    */tests/*
    */venv/*
    */settings/*
    manage.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = logs/coverage_html
```

### GitHub Actions
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: python manage.py test tests.unit
    
    - name: Run integration tests
      run: python manage.py test tests.integration
    
    - name: Generate coverage
      run: |
        coverage run --source='.' manage.py test
        coverage xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 📈 Métriques et Objectifs

### Couverture de Code
- **Unit tests** : > 90%
- **Integration tests** : > 80%
- **Global coverage** : > 85%

### Performance Benchmarks
- **Unit tests** : < 30 secondes total
- **Integration tests** : < 2 minutes total
- **Performance tests** : < 5 minutes total
- **Functional tests** : < 10 minutes total

### Qualité Code
- **PEP 8** compliance : 100%
- **Type hints** : > 80%
- **Docstrings** : > 90%
- **Cyclomatic complexity** : < 10

## 🔧 Outils et Intégrations

### Test Runners
- **Django TestCase** : Tests de base
- **pytest-django** : Fonctionnalités avancées
- **nose2** : Alternative runner

### Assertions Avancées
```python
from django.test import TestCase
from django.test.utils import assertNumQueries

class AdvancedTest(TestCase):
    def test_with_custom_assertions(self):
        # Vérification nombre de queries
        with self.assertNumQueries(2):
            list(User.objects.all())
        
        # Vérification logs
        with self.assertLogs('extranet.views', level='INFO') as log:
            response = self.client.get('/extranet/')
            self.assertIn('Dashboard accessed', log.output[0])
        
        # Vérification emails
        from django.core import mail
        # ... trigger email sending
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nouvelle demande', mail.outbox[0].subject)
```

### Browser Testing (Selenium)
```python
# tests/functional/test_browser.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

class BrowserTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_login_workflow(self):
        self.selenium.get(f'{self.live_server_url}/extranet/')
        # Test complet avec interactions navigateur
```

## 📚 Ressources

### Documentation
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/) (pour fixtures)

### Best Practices
- Tests AAA (Arrange, Act, Assert)
- One assertion per test
- Descriptive test names
- Fast feedback loop
- Continuous integration
