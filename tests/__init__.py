# Tests pour ICTGROUP Website

"""
Suite de tests pour l'application ICTGROUP Website.

Structure des tests :
├── unit/              # Tests unitaires rapides
│   ├── test_models.py         # Tests modèles extranet
│   ├── test_forms.py          # Tests formulaires extranet
│   └── test_intranet_models.py # Tests modèles intranet
├── integration/       # Tests d'intégration
│   ├── test_views.py          # Tests vues extranet
│   ├── test_auth.py           # Tests authentification extranet
│   └── test_intranet_views.py  # Tests vues intranet
├── functional/        # Tests fonctionnels end-to-end
│   └── test_intranet_functional.py # Tests workflows intranet
└── performance/       # Tests de performance
    └── performance_tests.py   # Tests performance extranet

Exécution des tests :
- Tous les tests : python manage.py test
- Tests unitaires : python manage.py test tests.unit
- Tests intégration : python manage.py test tests.integration
- Tests fonctionnels : python manage.py test tests.functional
- Tests performance : python manage.py test tests.performance
"""

# Imports pour faciliter l'exécution des tests
from .unit.test_models import *
from .unit.test_forms import *
from .unit.test_intranet_models import *
from .integration.test_views import *
from .integration.test_auth import *
from .integration.test_intranet_views import *
from .functional.test_intranet_functional import *
from .performance.performance_tests import *
