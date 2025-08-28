#!/usr/bin/env python3
"""
Test simple de navigation pour la page utilisateurs
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ictgroup.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_user_admin_navigation():
    print("🔍 TEST DE NAVIGATION - PAGE UTILISATEURS")
    print("=" * 50)
    
    # Créer un client de test
    client = Client()
    
    # Trouver un utilisateur admin
    admin = User.objects.filter(is_superuser=True).first()
    
    if not admin:
        print("❌ Aucun admin trouvé")
        return
    
    print(f"👤 Admin trouvé: {admin.username}")
    
    # Se connecter
    client.force_login(admin)
    print("🔑 Connexion forcée réussie")
    
    # Accéder à la page utilisateurs
    response = client.get('/extranet/utilisateurs/')
    print(f"📡 Requête vers /extranet/utilisateurs/")
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print(f"📏 Taille du contenu: {len(content)} caractères")
        
        # Vérifications de navigation
        checks = {
            'Header présent': '<header' in content,
            'Navigation principale': 'Menu principal' in content,
            'Navigation mobile': 'Menu mobile' in content,
            'Bouton hamburger': 'mobile-menu-btn' in content,
            'Logo ICTGROUP': 'logo-ictgroup' in content or 'ICTGROUP' in content,
            'Classes Tailwind': 'bg-gradient' in content,
            'JavaScript': '<script' in content,
        }
        
        print("\n🔍 Vérifications de navigation:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {check}: {status}")
        
        # Vérifier les blocs de template
        template_blocks = {
            'Block content fermé': '{% endblock %}' in content,
            'CSS séparé': '<style>' in content,
            'JS séparé': '<script>' in content,
        }
        
        print("\n🎨 Structure de template:")
        for check, result in template_blocks.items():
            status = "✅" if result else "❌"
            print(f"   {check}: {status}")
            
        # Extraire les premiers éléments de navigation
        print("\n📋 Début du HTML:")
        lines = content.split('\n')[:15]
        for i, line in enumerate(lines, 1):
            clean_line = line.strip()
            if clean_line:
                print(f"   {i:2}: {clean_line[:70]}{'...' if len(clean_line) > 70 else ''}")
        
    else:
        print(f"❌ Erreur HTTP {response.status_code}")
        print("📄 Contenu d'erreur:")
        print(response.content.decode('utf-8')[:500])
    
    print("\n🏁 Test terminé")

if __name__ == '__main__':
    test_user_admin_navigation()
