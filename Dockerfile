# Utilise l'image officielle de Python 3.11 basée sur Debian Slim Buster
FROM python:3.11-slim-buster

# Définit le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Copie le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installe les dépendances Python spécifiées dans requirements.txt
# --no-cache-dir : Ne stocke pas les fichiers de cache pip pour réduire la taille de l'image
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le contenu du dossier 'app' de l'hôte vers le répertoire '/app' du conteneur
COPY ./app /app

# Collecte les fichiers statiques Django pour la production
RUN python manage.py collectstatic --noinput || true

# Expose le port 8000, sur lequel l'application Django s'exécutera
EXPOSE 8000

# Commande par défaut pour démarrer l'application en production avec Gunicorn
CMD ["gunicorn", "ictgroup.wsgi:application", "--bind", "0.0.0.0:8000"]

# Pour le développement local avec docker-compose, cette commande est souvent écrasée.
# Pour la production (par exemple sur Fly.io), cette commande peut être utilisée avec Gunicorn.
# Un fichier .dockerignore est recommandé pour éviter de copier des fichiers inutiles dans l'image.