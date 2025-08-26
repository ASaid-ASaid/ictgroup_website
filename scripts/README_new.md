# 🛠️ Scripts ICT Group Website

*Collection de scripts pour l'administration et la maintenance*

## 📁 **Structure des Scripts**

### 🚀 **Déploiement** (`deployment/`)
Scripts pour le déploiement et la configuration en production

- **`deploy_fly.sh`** - Déploiement automatique sur Fly.io
- **`configure_gandi_domain.sh`** - Configuration DNS chez Gandi
- **`submit_to_search_engines.sh`** - Soumission aux moteurs de recherche
- **`setup-github-secrets.sh`** - Configuration des secrets GitHub

```bash
# Déploiement complet
./deployment/deploy_fly.sh

# Configuration DNS
./deployment/configure_gandi_domain.sh --domain ictgroup.fr
```

---

### 🔧 **Maintenance** (`maintenance/`)
Scripts pour la maintenance et l'optimisation du système

- **`optimize_project.sh`** - ⭐ Script d'optimisation global
- **`clean_cache.sh`** - Nettoyage du cache système
- **`maintain_scripts.sh`** - Maintenance des scripts
- **`monitor_certs.sh`** - Surveillance des certificats SSL

```bash
# Optimisation complète (recommandé hebdomadaire)
./maintenance/optimize_project.sh all

# Nettoyage du cache
./maintenance/clean_cache.sh
```

---

### 💻 **Développement** (`development/`)
Scripts pour l'environnement de développement

- **`install-git-hooks.sh`** - Installation des hooks Git
- **`prepare_commit.sh`** - Préparation des commits
- **`run_ci_local.sh`** - Test CI en local

```bash
# Configuration de l'environnement dev
./development/install-git-hooks.sh

# Test avant commit
./development/run_ci_local.sh
```

---

### 📊 **Import/Export** (`import_export/`)
Scripts pour la gestion des données

- **`import_new_users.py`** - Import d'utilisateurs depuis CSV
- **`export_to_csv.py`** - Export des données en CSV

```bash
# Import d'utilisateurs (préférer la commande Django)
python manage.py import_update_users --file data.csv --dry-run

# Export des données
python import_export/export_to_csv.py
```

---

## 🎯 **Scripts Principaux à Connaître**

### **1. Optimisation Globale** ⭐
```bash
./maintenance/optimize_project.sh all
```
- Nettoyage complet du système
- Optimisation de la base de données
- Réchauffement du cache
- Analyse des performances

### **2. Import d'Utilisateurs** 👥
```bash
# Via la commande Django (recommandé)
python manage.py import_update_users --file users.csv --dry-run
python manage.py import_update_users --file users.csv --overwrite

# Format CSV requis :
# username,nom,prenom,days_acquired,days_taken,days_carry_over,site,mail,password,role,manager,rh
```

### **3. Déploiement en Production** 🚀
```bash
./deployment/deploy_fly.sh
```

---

## 📋 **Utilisation des Scripts**

### **Permissions**
```bash
# Rendre les scripts exécutables
chmod +x scripts/**/*.sh
```

### **Variables d'Environnement**
Certains scripts nécessitent des variables d'environnement :
```bash
export FLY_API_TOKEN="your-token"
export GANDI_API_KEY="your-key"
```

### **Logs**
Les scripts génèrent des logs dans `/tmp/` ou `logs/` selon le script.

---

## 🔒 **Sécurité**

### **Scripts Sensibles**
- `setup-github-secrets.sh` - Contient des secrets
- `configure_gandi_domain.sh` - Utilise des API keys
- `deploy_fly.sh` - Accès aux serveurs de production

### **Bonnes Pratiques**
- ✅ Toujours tester avec `--dry-run` quand disponible
- ✅ Vérifier les permissions avant exécution
- ✅ Sauvegarder avant les scripts de modification
- ✅ Vérifier les logs après exécution

---

## 📈 **Maintenance Recommandée**

### **Quotidienne**
```bash
# Vérification rapide (manuel)
./maintenance/monitor_certs.sh
```

### **Hebdomadaire**
```bash
# Optimisation complète
./maintenance/optimize_project.sh all
```

### **Mensuelle**
```bash
# Import des nouveaux utilisateurs
python manage.py import_update_users --file monthly_users.csv --overwrite

# Nettoyage approfondi
./maintenance/clean_cache.sh --deep
```

### **Trimestrielle**
```bash
# Maintenance des scripts
./maintenance/maintain_scripts.sh

# Mise à jour des dépendances
./development/run_ci_local.sh --update
```

---

## 🆘 **Dépannage**

### **Scripts qui ne s'exécutent pas**
```bash
# Vérifier les permissions
ls -la script_name.sh

# Rendre exécutable
chmod +x script_name.sh
```

### **Erreurs de dépendances**
```bash
# Vérifier l'environnement Python
python --version
pip list

# Activer l'environnement virtuel si nécessaire
source venv/bin/activate
```

### **Logs d'erreur**
```bash
# Vérifier les logs système
tail -f /tmp/script_name.log

# Logs Django
tail -f app/django.log
```

---

## 📞 **Support**

Pour toute question sur les scripts :
1. Vérifier cette documentation
2. Consulter les logs d'erreur
3. Contacter l'administrateur système

---

*🔄 Scripts mis à jour automatiquement - Dernière révision : 26 août 2025*
