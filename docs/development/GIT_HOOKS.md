Git hooks (local) — installation & usage
=======================================

Ce dépôt fournit un hook `pre-commit` minimal pour aider le développement local.

Installation (une seule fois par développeur)

```bash
# Depuis la racine du repo
bash scripts/install-git-hooks.sh
```

Optionnel: utiliser `pre-commit` (recommandé)

```bash
# Installer pre-commit
pip install pre-commit
# Installer les hooks définis dans .pre-commit-config.yaml
pre-commit install
# Lancer pre-commit sur tous les fichiers (une fois)
pre-commit run --all-files
```

Que fait le hook ?
- Exécute `scripts/prepare_commit.sh` : formate (black, isort) et lance flake8 si installés.
- Lance un sous-ensemble de tests rapides via `pytest` si installé.

Personnalisation
- Tu peux modifier `.githooks/pre-commit` pour ajouter d'autres checks.
- Si tu utilises `pre-commit` (framework), tu peux migrer ces checks dans `.pre-commit-config.yaml`.

Remarques
- Les hooks sont locaux : ils ne sont pas committés dans `.git/hooks`. Le script `install-git-hooks.sh` copie les hooks dans `.git/hooks` et définit les droits.
- Ne pas stocker de secrets dans les hooks.
