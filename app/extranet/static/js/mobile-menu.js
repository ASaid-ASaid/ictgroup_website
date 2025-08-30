// ICTGROUP Extranet - Mobile Menu JavaScript
document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    console.log('🔄 Mobile menu JavaScript loaded');

    // Elements
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const mobileMenuClose = document.getElementById('mobile-menu-close');

    // State
    let isMenuOpen = false;
    let isTransitioning = false;

    // Debug logging
    console.log('🔍 Mobile menu elements found:', {
        toggle: !!mobileMenuToggle,
        menu: !!mobileMenu,
        overlay: !!mobileMenuOverlay,
        close: !!mobileMenuClose
    });

    // Initialize
    function init() {
        if (!mobileMenuToggle || !mobileMenu) {
            console.error('❌ Mobile menu elements not found - menu will not work');
            return;
        }

        console.log('✅ Mobile menu initialized successfully');

        // Event listeners
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🖱️ Hamburger clicked');
            toggleMenu();
        });

        if (mobileMenuClose) {
            mobileMenuClose.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('❌ Close button clicked');
                closeMenu();
            });
        }

        if (mobileMenuOverlay) {
            mobileMenuOverlay.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('� Overlay clicked');
                closeMenu();
            });
        }

        // Submenu toggles
        document.querySelectorAll('.submenu-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('📂 Submenu toggle clicked:', this.getAttribute('data-target'));
                toggleSubmenu(this);
            });
        });

        // Window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768 && isMenuOpen) {
                console.log('� Window resized to desktop size, closing menu');
                closeMenu();
            }
        });
    }

    // Toggle menu
    function toggleMenu() {
        if (isTransitioning) {
            console.log('⏳ Menu is transitioning, ignoring click');
            return;
        }

        if (isMenuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    // Open menu
    function openMenu() {
        if (isMenuOpen || isTransitioning) {
            console.log('🚫 Menu already open or transitioning, skipping');
            return;
        }

        console.log('🔓 Opening mobile menu');
        isTransitioning = true;
        isMenuOpen = true;

        // Show elements with inline styles
        if (mobileMenu) {
            mobileMenu.style.transform = 'translateX(0)';
            mobileMenu.style.right = '0';
            console.log('✅ Menu opened with inline styles');
        }

        if (mobileMenuOverlay) {
            mobileMenuOverlay.style.display = 'block';
            mobileMenuOverlay.style.opacity = '1';
            console.log('✅ Overlay shown');
        }

        // Update toggle button
        if (mobileMenuToggle) {
            mobileMenuToggle.classList.add('active');
            mobileMenuToggle.setAttribute('aria-expanded', 'true');
            console.log('✅ Toggle button updated');
        }

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Reset transition flag
        setTimeout(() => {
            isTransitioning = false;
            console.log('✨ Menu open transition completed');
        }, 300);

        console.log('🎉 Mobile menu opened successfully');
    }

    // Close menu
    function closeMenu() {
        if (!isMenuOpen || isTransitioning) {
            console.log('🚫 Menu already closed or transitioning, skipping');
            return;
        }

        console.log('🔒 Closing mobile menu');
        isTransitioning = true;
        isMenuOpen = false;

        // Hide elements with inline styles
        if (mobileMenu) {
            mobileMenu.style.transform = 'translateX(100%)';
            mobileMenu.style.right = '-320px';
            console.log('✅ Menu closed with inline styles');
        }

        if (mobileMenuOverlay) {
            mobileMenuOverlay.style.display = 'none';
            mobileMenuOverlay.style.opacity = '0';
            console.log('✅ Overlay hidden');
        }

        // Update toggle button
        if (mobileMenuToggle) {
            mobileMenuToggle.classList.remove('active');
            mobileMenuToggle.setAttribute('aria-expanded', 'false');
            console.log('✅ Toggle button updated');
        }

        // Restore body scroll
        document.body.style.overflow = '';

        // Close all submenus
        document.querySelectorAll('.submenu.open').forEach(submenu => {
            submenu.classList.remove('open');
            console.log('📂 Closed submenu:', submenu.id);
        });

        document.querySelectorAll('.chevron.rotated').forEach(chevron => {
            chevron.classList.remove('rotated');
            console.log('🔄 Reset chevron rotation');
        });

        // Reset transition flag
        setTimeout(() => {
            isTransitioning = false;
            console.log('✨ Menu close transition completed');
        }, 300);

        console.log('🎉 Mobile menu closed successfully');
    }

    // Initialize on load
    init();

    // Toggle submenu
    function toggleSubmenu(button) {
        const targetId = button.getAttribute('data-target');
        const submenu = document.getElementById(targetId);
        const chevron = button.querySelector('.chevron');

        if (!submenu) {
            console.warn('⚠️ Submenu not found:', targetId);
            return;
        }

        const isOpen = submenu.classList.contains('open');
        console.log('📂 Toggling submenu:', targetId, isOpen ? 'close' : 'open');

        // Close all other submenus
        document.querySelectorAll('.submenu.open').forEach(s => {
            if (s.id !== targetId) {
                s.classList.remove('open');
                const otherChevron = s.closest('.submenu-toggle').querySelector('.chevron');
                if (otherChevron) otherChevron.classList.remove('rotated');
            }
        });

        // Toggle current submenu
        if (!isOpen) {
            submenu.classList.add('open');
            if (chevron) chevron.classList.add('rotated');
            console.log('📂 Submenu opened:', targetId);
        } else {
            submenu.classList.remove('open');
            if (chevron) chevron.classList.remove('rotated');
            console.log('📂 Submenu closed:', targetId);
        }
    }
});
