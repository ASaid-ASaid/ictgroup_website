"""
Test simple pour diagnostiquer le problème de navigation - Django seulement
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from extranet.models import UserProfile


def run_simple_navigation_test():
    """Test simple de navigation sans dépendances externes"""
    print("🚀 DIAGNOSTIC SIMPLE DE LA NAVIGATION")
    print("=" * 50)
    
    # Créer un client de test
    client = Client()
    
    try:
        # Créer un utilisateur admin de test
        admin_user = User.objects.create_user(
            username='admin_test_nav',
            password='testpass123',
            email='admin@ictgroup.com',
            is_superuser=True,
            is_staff=True
        )
        
        # Créer le profil utilisateur
        admin_profile = UserProfile.objects.create(
            user=admin_user,
            role='admin',
            site='France',
            manager=None
        )
        
        print("✅ Utilisateur admin créé")
        
        # Test 1: Accès sans authentification
        print("\n🔍 Test 1: Accès sans authentification")
        response = client.get(reverse('extranet:user_admin'))
        print(f"   Status code: {response.status_code}")
        print(f"   Redirection: {response.get('Location', 'Aucune')}")
        
        # Test 2: Accès avec authentification admin
        print("\n🔍 Test 2: Accès avec admin")
        login_success = client.login(username='admin_test_nav', password='testpass123')
        print(f"   Login réussi: {login_success}")
        
        if login_success:
            response = client.get(reverse('extranet:user_admin'))
            print(f"   Status code: {response.status_code}")
            print(f"   Taille réponse: {len(response.content)} bytes")
            print(f"   Content-Type: {response.get('Content-Type', 'Non défini')}")
            
            # Test 3: Analyser le contenu HTML brut
            print("\n🔍 Test 3: Analyse du contenu HTML")
            content = response.content.decode('utf-8')
            
            # Rechercher les éléments de navigation critiques
            navigation_elements = {
                'header': '<header' in content,
                'nav_principal': 'aria-label="Menu principal"' in content,
                'nav_mobile': 'aria-label="Menu mobile"' in content,
                'bouton_hamburger': 'mobile-menu-btn' in content,
                'logo': 'logo-ictgroup' in content,
                'tailwind_classes': 'bg-gradient-to-r' in content or 'flex' in content,
                'javascript': '<script' in content,
            }
            
            print("   Éléments trouvés:")
            for element, found in navigation_elements.items():
                status = "✅" if found else "❌"
                print(f"      {element}: {status}")
            
            # Test 4: Rechercher des erreurs dans le HTML
            print("\n🔍 Test 4: Recherche d'erreurs")
            error_indicators = {
                'erreur_template': 'TemplateSyntaxError' in content or 'TemplateDoesNotExist' in content,
                'erreur_css': 'css' in content.lower() and 'error' in content.lower(),
                'erreur_js': 'javascript' in content.lower() and 'error' in content.lower(),
                'contenu_vide': len(content.strip()) < 1000,
                'balises_fermees': content.count('<') == content.count('>'),
            }
            
            print("   Indicateurs d'erreur:")
            for indicator, detected in error_indicators.items():
                status = "⚠️" if detected else "✅"
                print(f"      {indicator}: {status}")
            
            # Test 5: Extraire les premières lignes du HTML
            print("\n🔍 Test 5: Début du HTML généré")
            lines = content.split('\n')[:20]
            for i, line in enumerate(lines, 1):
                line_clean = line.strip()
                if line_clean:
                    print(f"   {i:2d}: {line_clean[:80]}{'...' if len(line_clean) > 80 else ''}")
            
            # Test 6: Vérifier les includes CSS et JS critiques
            print("\n🔍 Test 6: Ressources critiques")
            css_js_elements = {
                'tailwind_cdn': 'tailwindcss' in content,
                'static_css': 'css' in content and 'static' in content,
                'static_js': 'js' in content and 'static' in content,
                'base_template': 'base.html' in str(response.templates) if hasattr(response, 'templates') else False,
            }
            
            print("   Ressources détectées:")
            for resource, found in css_js_elements.items():
                status = "✅" if found else "❌"
                print(f"      {resource}: {status}")
        
        # Nettoyage
        admin_user.delete()
        print("\n🧹 Nettoyage effectué")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 DIAGNOSTIC TERMINÉ")


if __name__ == '__main__':
    run_simple_navigation_test()
