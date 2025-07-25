# =====================
# Vues principales de l'app 'vitrine'
# Chaque fonction gère une page publique du site vitrine
# =====================

from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

# Vue pour la page d'accueil de la vitrine
def index(request):
    """
    Affiche la page d'accueil de la vitrine.
    """
    logger.info(f"[index] Page d'accueil appelée par {request.user if request.user.is_authenticated else 'anonyme'}")
    return render(request, 'vitrine/index.html', {'company_name': 'ICTGROUP'})

# Ajoutez ici d'autres vues pour la vitrine si besoin (services, contact, etc.)
