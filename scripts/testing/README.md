# 🧪 Scripts de Test

Scripts pour les tests automatisés et la validation du code.

## 📁 Contenu

### 🔄 run_ci_local.sh
Exécution des tests CI en local
- Tests unitaires Django
- Tests d'intégration
- Vérification du code
- Génération de rapports

## 🔧 Utilisation

```bash
# Tous les tests
./manage.sh test

# Tests CI locaux
./scripts/testing/run_ci_local.sh

# Tests spécifiques
./manage.sh test:unit
./manage.sh test:integration
./manage.sh test:performance
```

## 📊 Types de Tests

### Tests Unitaires
- Models Django
- Formulaires
- Utilitaires

### Tests d'Intégration
- Vues Django
- API Supabase
- Authentification

### Tests de Performance
- Temps de réponse
- Utilisation mémoire
- Requêtes base de données

### Tests Fonctionnels
- Parcours utilisateur
- Interface web
- Workflows complets

## 📋 Configuration

Les tests utilisent une base de données SQLite en mémoire pour la rapidité.
Configuration dans `app/ictgroup/settings.py` section `TESTING`.

## 📈 Rapports

Les rapports de test sont générés dans:
- `logs/test_results.xml` - Résultats JUnit
- `logs/coverage.html` - Couverture de code
- `logs/performance.json` - Métriques performance
