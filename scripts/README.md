# 🔧 Scripts d'Automatisation ICTGROUP Website

Ce dossier contient les scripts d'automatisation et de maintenance du projet.

## 📋 Scripts Disponibles

### 🧹 Maintenance et Nettoyage
- **`clean_cache.sh`** - Nettoyage des caches Python, Django et Docker
  - Usage: `./manage.sh clean:cache`
  - Nettoie les fichiers `.pyc`, `__pycache__`, logs anciens
  - Fonctionne en local et dans les containers Docker

### 🔍 Diagnostic
- **`debug_static.sh`** - Diagnostic des fichiers statiques
  - Usage: `./manage.sh debug:static`
  - Vérifie les fichiers CSS/JS
  - Teste collectstatic
  - Propose des solutions aux problèmes

### 🚀 Déploiement
- **`deploy_fly.sh`** - Déploiement sur Fly.io
  - Usage: `./manage.sh deploy:fly`
  - Installation automatique de Fly CLI
  - Configuration des secrets
  - Création de la base de données PostgreSQL

### 🛠️ Maintenance
- **`maintain_scripts.sh`** - Maintenance du dossier scripts
  - Usage: `./manage.sh maintain:scripts`
  - Vérifie les scripts utilisés/inutilisés
  - Contrôle des permissions
  - Vérification de la syntaxe

## 🎯 Utilisation Recommandée

### Via le Script Central
```bash
# Utilisation recommandée (via manage.sh)
./manage.sh clean:cache      # Nettoyage
./manage.sh debug:static     # Diagnostic
./manage.sh deploy:fly       # Déploiement
./manage.sh maintain:scripts # Maintenance
```

### Exécution Directe
```bash
# Exécution directe (non recommandée)
./scripts/clean_cache.sh
./scripts/debug_static.sh
./scripts/deploy_fly.sh
./scripts/maintain_scripts.sh
```

## 📝 Standards des Scripts

### Structure Requise
- **Shebang** : `#!/bin/bash`
- **Set options** : `set -e` (arrêt sur erreur)
- **Couleurs** : Utilisation des codes ANSI
- **Logging** : Fonctions `log_info()`, `log_warn()`, `log_error()`
- **Documentation** : Header avec description et usage

### Exemple de Template
```bash
#!/bin/bash

# =============================================================================
# Description du script
# =============================================================================
# Description: Ce que fait le script
# Usage: ./scripts/nom_script.sh
# Auteur: ICTGROUP Development Team
# =============================================================================

set -e

# Configuration des couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Logique du script...
```

## 🚨 Scripts Supprimés/Obsolètes

### Scripts Nettoyés
- **`deploy_docker.sh`** ❌ **SUPPRIMÉ**
  - Raison: Obsolète, remplacé par manage.sh
  - Alternative: `./manage.sh start` pour Docker local

## 🔄 Maintenance Automatique

Le script `maintain_scripts.sh` vérifie automatiquement :
- ✅ Scripts utilisés vs inutilisés
- ✅ Permissions d'exécution
- ✅ Syntaxe bash
- ✅ Références dans manage.sh
- ✅ Standards de codage

## 📊 Intégration avec manage.sh

Tous les scripts sont intégrés dans le système central `manage.sh` :

| Script | Commande manage.sh | Description |
|--------|-------------------|-------------|
| `clean_cache.sh` | `clean:cache` | Nettoyage caches |
| `debug_static.sh` | `debug:static` | Diagnostic statiques |
| `deploy_fly.sh` | `deploy:fly` | Déploiement Fly.io |
| `maintain_scripts.sh` | `maintain:scripts` | Maintenance scripts |

## 🆘 Dépannage

### Script non exécutable
```bash
chmod +x scripts/nom_script.sh
```

### Erreur de syntaxe
```bash
bash -n scripts/nom_script.sh  # Vérification syntaxe
```

### Script non trouvé
```bash
ls -la scripts/                # Lister les scripts
./manage.sh maintain:scripts   # Vérification complète
```

---

<div align="center">

**[🏠 Retour au README](../README.md) • [🛠️ Guide manage.sh](../README.md#-script-central-managesh)**

*Scripts maintenus et optimisés - ICTGROUP Team*

</div>
