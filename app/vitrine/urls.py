# =====================
# Définition des routes (URLs) pour l'application vitrine
# Chaque URL correspond à une vue (fonction) dans views.py
# =====================

from django.urls import path

from . import views

# Nom de l'application pour la gestion des espaces de noms d'URL
app_name = "vitrine"

urlpatterns = [
    # URL pour la page d'accueil de la vitrine
    path("", views.index, name="index"),
    # Page services pour le SEO
    path("services/", views.services, name="services"),
    # Ajoutez ici d'autres URLs pour la vitrine (services, contact, etc.)
]
