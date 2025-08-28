"""
Test pour diagnostiquer le problème de navigation sur la page utilisateurs
"""
import os
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import override_settings
from bs4 import BeautifulSoup

# Configuration Django pour les tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ictgroup.settings')
django.setup()

from extranet.models import UserProfile


class NavigationIssueTest(TestCase):
    """Tests pour diagnostiquer les problèmes de navigation"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un utilisateur admin pour tester
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            email='admin@ictgroup.com',
            is_superuser=True,
            is_staff=True
        )
        
        # Créer le profil utilisateur
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            site='France',
            manager=None
        )
        
        # Créer un utilisateur normal
        self.normal_user = User.objects.create_user(
            username='user_test',
            password='testpass123',
            email='user@ictgroup.com'
        )
        
        self.normal_profile = UserProfile.objects.create(
            user=self.normal_user,
            role='employee',
            site='France',
            manager=self.admin_user
        )
    
    def test_user_admin_page_access(self):
        """Test d'accès à la page de gestion des utilisateurs"""
        print("\n🔍 Test d'accès à la page utilisateurs...")
        
        # Test sans authentification - doit rediriger vers login
        response = self.client.get(reverse('extranet:user_admin'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        print("✅ Redirection vers login pour utilisateur non authentifié")
        
        # Test avec utilisateur normal - doit être refusé
        self.client.login(username='user_test', password='testpass123')
        response = self.client.get(reverse('extranet:user_admin'))
        print(f"📊 Status code pour utilisateur normal: {response.status_code}")
        
        # Test avec admin - doit fonctionner
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('extranet:user_admin'))
        self.assertEqual(response.status_code, 200)
        print("✅ Accès autorisé pour admin")
        
        return response
    
    def test_navigation_structure(self):
        """Test de la structure de navigation"""
        print("\n🧭 Test de la structure de navigation...")
        
        # Se connecter en tant qu'admin
        self.client.login(username='admin_test', password='testpass123')
        
        # Récupérer la page utilisateurs
        response = self.client.get(reverse('extranet:user_admin'))
        
        # Parser le HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier la présence de la navigation principale
        nav_main = soup.find('nav', {'aria-label': 'Menu principal'})
        if nav_main:
            print("✅ Navigation principale trouvée")
        else:
            print("❌ Navigation principale manquante")
            
        # Vérifier la navigation mobile
        nav_mobile = soup.find('nav', {'aria-label': 'Menu mobile'})
        if nav_mobile:
            print("✅ Navigation mobile trouvée")
        else:
            print("❌ Navigation mobile manquante")
            
        # Vérifier le bouton hamburger
        hamburger_btn = soup.find('button', {'id': 'mobile-menu-btn'})
        if hamburger_btn:
            print("✅ Bouton hamburger trouvé")
        else:
            print("❌ Bouton hamburger manquant")
            
        # Vérifier le header
        header = soup.find('header')
        if header:
            print("✅ Header trouvé")
            print(f"📋 Classes du header: {header.get('class', 'Aucune classe')}")
        else:
            print("❌ Header manquant")
            
        return soup
    
    def test_css_and_js_loading(self):
        """Test du chargement des ressources CSS et JS"""
        print("\n📦 Test des ressources CSS/JS...")
        
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('extranet:user_admin'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier les feuilles de style
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        print(f"📄 Nombre de feuilles CSS: {len(css_links)}")
        
        for css in css_links:
            href = css.get('href', '')
            print(f"   - {href}")
            
        # Vérifier les scripts JavaScript
        js_scripts = soup.find_all('script')
        print(f"📄 Nombre de scripts JS: {len(js_scripts)}")
        
        for script in js_scripts:
            src = script.get('src', '')
            if src:
                print(f"   - {src}")
        
        # Vérifier spécifiquement Tailwind CSS
        tailwind_found = any('tailwind' in css.get('href', '').lower() for css in css_links)
        if tailwind_found:
            print("✅ Tailwind CSS détecté")
        else:
            print("⚠️  Tailwind CSS non détecté - peut affecter la navigation")
    
    def test_navigation_visibility_classes(self):
        """Test des classes CSS pour la visibilité de la navigation"""
        print("\n🎨 Test des classes CSS de navigation...")
        
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('extranet:user_admin'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Vérifier les classes de navigation desktop
        nav_desktop = soup.find('nav', {'aria-label': 'Menu principal'})
        if nav_desktop:
            classes = nav_desktop.get('class', [])
            print(f"🖥️  Classes navigation desktop: {classes}")
            
            # Vérifier si elle est cachée sur mobile
            if 'hidden' in classes and 'md:flex' in classes:
                print("✅ Navigation desktop correctement cachée sur mobile")
            else:
                print("⚠️  Navigation desktop pourrait avoir des problèmes de visibilité")
        
        # Vérifier les classes de navigation mobile
        nav_mobile = soup.find('nav', {'aria-label': 'Menu mobile'})
        if nav_mobile:
            classes = nav_mobile.get('class', [])
            print(f"📱 Classes navigation mobile: {classes}")
            
            # Vérifier si elle est cachée par défaut
            if 'hidden' in classes or 'md:hidden' in classes:
                print("✅ Navigation mobile correctement configurée")
            else:
                print("⚠️  Navigation mobile pourrait être toujours visible")
    
    def test_full_navigation_diagnostic(self):
        """Test complet de diagnostic de navigation"""
        print("\n🔬 DIAGNOSTIC COMPLET DE LA NAVIGATION")
        print("=" * 50)
        
        # Exécuter tous les tests
        response = self.test_user_admin_page_access()
        soup = self.test_navigation_structure()
        self.test_css_and_js_loading()
        self.test_navigation_visibility_classes()
        
        # Rapport final
        print("\n📋 RAPPORT FINAL:")
        print("-" * 30)
        
        # Vérifier les éléments critiques
        critical_elements = {
            'header': soup.find('header'),
            'nav_main': soup.find('nav', {'aria-label': 'Menu principal'}),
            'nav_mobile': soup.find('nav', {'aria-label': 'Menu mobile'}),
            'hamburger': soup.find('button', {'id': 'mobile-menu-btn'}),
            'logo': soup.find('img', {'class': 'logo-ictgroup'}) or soup.find('img'),
        }
        
        for element_name, element in critical_elements.items():
            status = "✅ PRÉSENT" if element else "❌ MANQUANT"
            print(f"{element_name.upper()}: {status}")
        
        # Analyser le contenu du template
        print(f"\n📊 Taille de la réponse: {len(response.content)} bytes")
        print(f"📊 Type de contenu: {response.get('Content-Type', 'Non défini')}")
        
        # Rechercher des erreurs potentielles dans le HTML
        if 'error' in response.content.decode().lower():
            print("⚠️  Erreurs potentielles détectées dans le HTML")
        
        if len(response.content) < 1000:
            print("⚠️  Réponse très courte - template potentiellement cassé")


def run_navigation_tests():
    """Fonction pour exécuter les tests de navigation"""
    print("🚀 DÉMARRAGE DES TESTS DE NAVIGATION")
    print("=" * 60)
    
    # Créer une instance de test
    test_instance = NavigationIssueTest()
    test_instance.setUp()
    
    try:
        # Exécuter le diagnostic complet
        test_instance.test_full_navigation_diagnostic()
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DU TEST: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 TESTS TERMINÉS")


if __name__ == '__main__':
    run_navigation_tests()
