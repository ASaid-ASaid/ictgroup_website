// Mobile Menu JavaScript - ICT Group Extranet
document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Variables
    let mobileMenuBtn = null;
    let mobileMenu = null;
    let hamburgerLines = null;
    let isMenuOpen = false;
    
    // Initialize mobile menu after DOM is loaded
    initializeMobileMenu();
    
    function initializeMobileMenu() {
        // Get elements
        mobileMenuBtn = document.getElementById('mobile-menu-btn');
        mobileMenu = document.getElementById('mobile-menu');
        hamburgerLines = document.querySelectorAll('.hamburger-line');
        
        // Check if elements exist
        if (!mobileMenuBtn || !mobileMenu) {
            console.warn('Mobile menu elements not found');
            return;
        }
        
        // Force initial hidden state
        mobileMenu.classList.add('hidden');
        mobileMenu.classList.remove('visible');
        isMenuOpen = false;
        
        // Add event listeners
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
        
        // Add click event for mobile submenu toggles
        const submenuBtns = document.querySelectorAll('.mobile-submenu-btn');
        submenuBtns.forEach(btn => {
            btn.addEventListener('click', toggleMobileSubmenu);
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (isMenuOpen && !mobileMenu.contains(event.target) && !mobileMenuBtn.contains(event.target)) {
                closeMobileMenu();
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768 && isMenuOpen) {
                closeMobileMenu();
            }
        });
        
        console.log('Mobile menu initialized successfully');
    }
    
    function toggleMobileMenu() {
        console.log('Mobile menu toggle clicked');
        if (isMenuOpen) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }
    
    function openMobileMenu() {
        console.log('Opening mobile menu');
        isMenuOpen = true;
        
        // Show menu with explicit classes
        mobileMenu.classList.remove('hidden');
        mobileMenu.classList.add('visible');
        mobileMenu.classList.add('animate-slideDown');
        
        // Transform hamburger to X
        if (hamburgerLines.length >= 3) {
            hamburgerLines[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            hamburgerLines[1].style.opacity = '0';
            hamburgerLines[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
        }
        
        // Update aria attributes
        mobileMenuBtn.setAttribute('aria-expanded', 'true');
        mobileMenuBtn.setAttribute('aria-label', 'Fermer le menu');
        
        // Lock scroll on mobile
        if (window.innerWidth < 768) {
            document.body.style.overflow = 'hidden';
        }
    }
    
    function closeMobileMenu() {
        console.log('Closing mobile menu');
        isMenuOpen = false;
        
        // Hide menu with explicit classes
        mobileMenu.classList.add('hidden');
        mobileMenu.classList.remove('visible');
        mobileMenu.classList.remove('animate-slideDown');
        
        // Reset hamburger
        if (hamburgerLines.length >= 3) {
            hamburgerLines[0].style.transform = '';
            hamburgerLines[1].style.opacity = '';
            hamburgerLines[2].style.transform = '';
        }
        
        // Update aria attributes
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
        mobileMenuBtn.setAttribute('aria-label', 'Ouvrir le menu');
        
        // Unlock scroll
        document.body.style.overflow = '';
        
        // Close all submenus
        const openSubmenus = document.querySelectorAll('.mobile-submenu-content:not(.hidden)');
        openSubmenus.forEach(submenu => {
            submenu.classList.add('hidden');
            const chevron = submenu.parentElement.querySelector('.mobile-chevron');
            if (chevron) {
                chevron.style.transform = '';
            }
        });
    }
    
    function toggleMobileSubmenu(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const btn = event.currentTarget;
        const submenu = btn.nextElementSibling;
        const chevron = btn.querySelector('.mobile-chevron');
        
        if (!submenu) return;
        
        const isOpen = !submenu.classList.contains('hidden');
        
        // Close all other submenus first
        const allSubmenus = document.querySelectorAll('.mobile-submenu-content');
        const allChevrons = document.querySelectorAll('.mobile-chevron');
        
        allSubmenus.forEach(menu => menu.classList.add('hidden'));
        allChevrons.forEach(icon => icon.style.transform = '');
        
        // Toggle current submenu
        if (!isOpen) {
            submenu.classList.remove('hidden');
            if (chevron) {
                chevron.style.transform = 'rotate(180deg)';
            }
        }
    }
    
    // Debug function
    function debugMobileMenu() {
        console.log('=== Mobile Menu Debug ===');
        console.log('Mobile menu button:', mobileMenuBtn);
        console.log('Mobile menu:', mobileMenu);
        console.log('Hamburger lines:', hamburgerLines.length);
        console.log('Menu open state:', isMenuOpen);
        console.log('Window width:', window.innerWidth);
    }
    
    // Expose debug function globally
    window.debugMobileMenu = debugMobileMenu;
});
