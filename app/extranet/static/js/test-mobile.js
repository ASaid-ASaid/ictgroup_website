// Test final - menu mobile fonctionnel
console.log('=== MENU MOBILE FINAL ===');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM chargé');

    const toggle = document.getElementById('mobile-menu-toggle');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');

    console.log('Éléments trouvés:', {
        toggle: !!toggle,
        menu: !!menu,
        overlay: !!overlay
    });

    if (!toggle || !menu) {
        console.error('Éléments manquants');
        return;
    }

    // Configuration du menu
    let isOpen = false;

    // Styles pour le menu (inline pour éviter les conflits CSS)
    menu.style.position = 'fixed';
    menu.style.top = '0';
    menu.style.right = '-320px'; // Commence caché
    menu.style.width = '320px';
    menu.style.height = '100vh';
    menu.style.background = 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)';
    menu.style.transition = 'right 0.3s ease';
    menu.style.zIndex = '1000';
    menu.style.padding = '20px';
    menu.style.boxShadow = '-5px 0 25px rgba(0, 0, 0, 0.3)';
    menu.style.overflowY = 'auto';

    // Contenu du menu
    menu.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.2);">
            <h2 style="color: white; font-size: 24px; font-weight: bold; margin: 0;">Menu</h2>
            <button id="mobile-menu-close" style="color: white; font-size: 28px; background: none; border: none; cursor: pointer; padding: 5px;">&times;</button>
        </div>
        <nav>
            <a href="#" style="display: block; color: white; text-decoration: none; padding: 15px; margin-bottom: 10px; border-radius: 8px; background: rgba(255,255,255,0.1); transition: background 0.2s;">🏠 Accueil</a>
            <a href="#" style="display: block; color: white; text-decoration: none; padding: 15px; margin-bottom: 10px; border-radius: 8px; background: rgba(255,255,255,0.1); transition: background 0.2s;">📋 Test 1</a>
            <a href="#" style="display: block; color: white; text-decoration: none; padding: 15px; margin-bottom: 10px; border-radius: 8px; background: rgba(255,255,255,0.1); transition: background 0.2s;">⚙️ Test 2</a>
        </nav>
    `;

    // Styles pour l'overlay
    if (overlay) {
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.background = 'rgba(0, 0, 0, 0.6)';
        overlay.style.zIndex = '999';
        overlay.style.opacity = '0';
        overlay.style.visibility = 'hidden';
        overlay.style.transition = 'opacity 0.3s ease, visibility 0.3s ease';
    }

    // Fonction pour ouvrir le menu
    function openMenu() {
        console.log('Ouverture du menu');
        isOpen = true;
        menu.style.right = '0';
        if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
        }
        document.body.style.overflow = 'hidden'; // Empêcher le scroll
    }

    // Fonction pour fermer le menu
    function closeMenu() {
        console.log('Fermeture du menu');
        isOpen = false;
        menu.style.right = '-320px';
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
        }
        document.body.style.overflow = ''; // Restaurer le scroll
    }

    // Event listeners
    toggle.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Clic sur toggle');
        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // Fermer avec le bouton X
    const closeBtn = document.getElementById('mobile-menu-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeMenu();
        });
    }

    // Fermer en cliquant sur l'overlay
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            e.preventDefault();
            closeMenu();
        });
    }

    // Fermer avec Échap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isOpen) {
            closeMenu();
        }
    });

    console.log('Menu mobile configuré avec succès !');

    // Test automatique après 3 secondes
    setTimeout(() => {
        console.log('Test automatique...');
        if (!isOpen) {
            openMenu();
            setTimeout(() => {
                closeMenu();
            }, 2000);
        }
    }, 3000);
});
