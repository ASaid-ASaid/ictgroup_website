"""
Configuration des URLs principales du projet ictgroup.
La liste `urlpatterns` achemine les URLs vers les vues appropriées.
Inclut les routes admin, vitrine et extranet.
"""
from django.contrib import admin
from django.urls import path, include # Importe include pour inclure les URLs d'autres applications
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # URL pour l'interface d'administration de Django
    path('', include('vitrine.urls')), # Inclut les URLs de l'application 'vitrine' pour la racine du site
    path('extranet/', include('extranet.urls')), # Inclut les URLs de l'application 'extranet'
]

# Ajoute la gestion des fichiers statiques en mode développement
# Ceci est nécessaire pour que les fichiers statiques soient servis par Django en mode DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
