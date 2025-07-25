# ICTGROUP Website

Ce projet est un site web d'entreprise basé sur Django, avec un extranet pour les employés et une vitrine publique.

---

## Structure du projet

- `app/vitrine` : Application vitrine (publique)
- `app/extranet` : Application extranet (employés)
- `app/ictgroup` : Configuration principale Django
- `static/` : Fichiers statiques globaux (images, CSS, JS)
- `logs/` : Fichiers de logs (à ajouter au .gitignore)
- `docker-compose.yml`, `Dockerfile` : Configuration Docker
- `.env.example` : Exemple de configuration d'environnement

---

## Lancement rapide

1. **Cloner le dépôt**
2. **Copier le fichier `.env.example` en `.env` et adapter les variables**
3. **Construire et lancer avec Docker**
   ```sh
   docker-compose up --build
   ```
4. **Accéder à l'application**
   - Vitrine : http://localhost:8000/
   - Extranet : http://localhost:8000/extranet/

---

## Variables d'environnement
Voir `.env.example` pour la configuration.

---

## Collecte des fichiers statiques
En production, les fichiers statiques sont collectés automatiquement dans l'image Docker.

---

## Bonnes pratiques
- Ne jamais commiter de vraies clés secrètes ou mots de passe.
- Ajouter des tests unitaires dans `tests/`.
- Utiliser un reverse proxy (Nginx) en production.
- Ajouter les dossiers `__pycache__/`, `*.pyc`, `logs/`, `.env` au `.gitignore`.

---

## Accès à l'interface graphique PostgreSQL (Adminer)

Pour gérer la base de données PostgreSQL via une interface web :

1. **Lancer les services Docker** (si ce n'est pas déjà fait) :
   ```sh
   docker-compose up --build
   ```
2. **Ouvrir Adminer dans votre navigateur** : [http://localhost:8080](http://localhost:8080)
3. **Renseigner les informations de connexion** :
   - **SGBD** : PostgreSQL
   - **Serveur** : db
   - **Utilisateur** : (valeur de `DB_USER` dans `.env`)
   - **Mot de passe** : (valeur de `DB_PASSWORD` dans `.env`)
   - **Base** : (valeur de `DB_NAME` dans `.env`)

Vous pouvez ainsi visualiser, éditer et administrer vos tables PostgreSQL facilement.

---

## Auteur
ahmed.said@ictgroup.fr
