"""
Configuration des URLs principales du projet ictgroup.
La liste `urlpatterns` achemine les URLs vers les vues appropriées.
Inclut les routes admin, vitrine et extranet.
"""

from django.contrib import admin
from django.urls import (
    path,
    include,
)  # Importe include pour inclure les URLs d'autres applications
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
import os

def health_check(request):
    """Health check endpoint for Fly.io"""
    return JsonResponse({'status': 'healthy'})

def robots_txt(request):
    """Serve robots.txt file"""
    content = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://ictgroup.fr/sitemap.xml

# Disallow admin pages
Disallow: /admin/
Disallow: /extranet/
Disallow: /static/admin/

# Allow specific static files
Allow: /static/css/
Allow: /static/js/
Allow: /static/img/

# Crawl delay
Crawl-delay: 1"""
    return HttpResponse(content, content_type='text/plain')

def sitemap_xml(request):
    """Generate sitemap.xml"""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://ictgroup.fr/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
        <lastmod>2025-08-23</lastmod>
    </url>
    <url>
        <loc>https://ictgroup.fr/#services</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://ictgroup.fr/#about</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://ictgroup.fr/#contact</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>"""
    return HttpResponse(content, content_type='application/xml')

urlpatterns = [
    path(
        "admin/", admin.site.urls
    ),  # URL pour l'interface d'administration de Django
    path(
        "", include("vitrine.urls")
    ),  # Inclut les URLs de l'application 'vitrine' pour la racine du site
    path(
        "extranet/", include("extranet.urls")
    ),  # Inclut les URLs de l'application 'extranet'
    path("health/", health_check, name="health_check"),  # Health check pour Fly.io
    path("robots.txt", robots_txt, name="robots_txt"),  # Robots.txt pour SEO
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),  # Sitemap pour SEO
]

# Ajoute la gestion des fichiers statiques en mode développement
# Ceci est nécessaire pour que les fichiers statiques soient servis par Django en mode DEBUG=True
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
