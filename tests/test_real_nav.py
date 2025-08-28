"""
Test de navigation avec vraie session Django (sans testserver)
"""


def test_navigation_real_session():
    """Test avec une vraie session Django"""
    print("🌐 TEST DE NAVIGATION - SESSION RÉELLE")
    print("=" * 50)
    
    from django.contrib.auth.models import User
    from django.contrib.sessions.models import Session
    from django.test import Client
    from django.urls import reverse
    from extranet.models import UserProfile
    import requests
    
    try:
        # Vérifier qu'on a accès aux vrais utilisateurs
        users_count = User.objects.count()
        print(f"👥 Utilisateurs en base: {users_count}")
        
        # Trouver un admin existant
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"👤 Admin trouvé: {admin_user.username}")
            
            # Tester avec une vraie requête HTTP au serveur local
            print("\n🌐 Test requête HTTP directe...")
            
            # Session de login
            session_response = requests.get('http://localhost:8000/extranet/login/')
            if session_response.status_code == 200:
                print("✅ Page de login accessible")
                
                # Vérifier la présence d'éléments dans le HTML de login
                content = session_response.text
                nav_elements = {
                    'header': '<header' in content,
                    'navigation': 'nav' in content,
                    'logo': 'logo' in content or 'ICTGROUP' in content,
                    'tailwind': 'bg-' in content or 'flex' in content,
                    'mobile_menu': 'mobile' in content,
                }
                
                print("📋 Éléments trouvés sur la page login:")
                for element, found in nav_elements.items():
                    status = "✅" if found else "❌"
                    print(f"   {element}: {status}")
                    
            else:
                print(f"❌ Erreur d'accès à login: {session_response.status_code}")
                
        else:
            print("❌ Aucun admin trouvé en base")
            
        # Tester le template de base directement
        print("\n📄 Test du template base...")
        from django.template.loader import get_template
        from django.template import Context
        
        try:
            base_template = get_template('extranet/base.html')
            print("✅ Template base.html trouvé")
            
            # Créer un contexte minimal
            context = {
                'user': admin_user if admin_user else None,
                'request': type('MockRequest', (), {
                    'user': admin_user if admin_user else None,
                    'method': 'GET',
                    'path': '/extranet/utilisateurs/'
                })()
            }
            
            # Tenter de rendre le template
            try:
                rendered = base_template.render(context)
                print(f"✅ Template rendu avec succès ({len(rendered)} caractères)")
                
                # Analyser le rendu
                base_elements = {
                    'doctype': '<!DOCTYPE html>' in rendered,
                    'html_tag': '<html' in rendered,
                    'header_tag': '<header' in rendered,
                    'nav_tag': '<nav' in rendered,
                    'tailwind_classes': 'bg-gradient' in rendered or 'flex' in rendered,
                    'mobile_menu': 'mobile-menu' in rendered,
                    'hamburger': 'hamburger' in rendered,
                }
                
                print("📋 Éléments dans template base rendu:")
                for element, found in base_elements.items():
                    status = "✅" if found else "❌"
                    print(f"   {element}: {status}")
                    
            except Exception as e:
                print(f"❌ Erreur rendu template: {str(e)}")
                
        except Exception as e:
            print(f"❌ Template base.html non trouvé: {str(e)}")
            
    except Exception as e:
        print(f"❌ ERREUR GÉNÉRALE: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 TEST TERMINÉ")


if __name__ == '__main__':
    test_navigation_real_session()
