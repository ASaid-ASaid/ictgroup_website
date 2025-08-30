/**
 * Intranet ICTGROUP - JavaScript
 * Gestion des interactions côté client
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    console.log('🏢 Intranet JavaScript loaded');

    // Initialisation
    initializeIntranet();

    function initializeIntranet() {
        // Gestion des filtres
        initializeFilters();

        // Gestion des modales
        initializeModals();

        // Gestion des confirmations
        initializeConfirmations();

        // Gestion des formulaires
        initializeForms();

        // Animations
        initializeAnimations();

        console.log('✅ Intranet initialized successfully');
    }

    // ========== GESTION DES FILTRES ==========

    function initializeFilters() {
        const filterForms = document.querySelectorAll('.filters-intranet form');

        filterForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(this);
                const params = new URLSearchParams();

                for (let [key, value] of formData.entries()) {
                    if (value.trim() !== '') {
                        params.append(key, value);
                    }
                }

                // Mettre à jour l'URL sans recharger la page
                const newUrl = `${window.location.pathname}?${params.toString()}`;
                window.location.href = newUrl;
            });
        });

        // Auto-submit des filtres select
        const filterSelects = document.querySelectorAll('.filters-intranet select');
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                const form = this.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            });
        });
    }

    // ========== GESTION DES MODALES ==========

    function initializeModals() {
        // Ouvrir les modales
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const modalId = this.getAttribute('data-modal');
                openModal(modalId);
            });
        });

        // Fermer les modales
        const modalClosers = document.querySelectorAll('[data-close-modal]');
        modalClosers.forEach(closer => {
            closer.addEventListener('click', function(e) {
                e.preventDefault();
                const modal = this.closest('.modal-intranet');
                if (modal) {
                    closeModal(modal.id);
                }
            });
        });

        // Fermer en cliquant sur l'overlay
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal-overlay')) {
                const modal = e.target.querySelector('.modal-intranet');
                if (modal) {
                    closeModal(modal.id);
                }
            }
        });

        // Fermer avec Échap
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal-intranet.show');
                openModals.forEach(modal => {
                    closeModal(modal.id);
                });
            }
        });
    }

    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';

            // Focus sur le premier élément focusable
            const focusable = modal.querySelector('input, select, textarea, button');
            if (focusable) {
                focusable.focus();
            }
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    // ========== GESTION DES CONFIRMATIONS ==========

    function initializeConfirmations() {
        const confirmButtons = document.querySelectorAll('[data-confirm]');

        confirmButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm') || 'Êtes-vous sûr ?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }

    // ========== GESTION DES FORMULAIRES ==========

    function initializeForms() {
        // Calcul automatique des totaux
        initializeCalculations();

        // Validation des formulaires
        initializeValidation();

        // Soumission AJAX pour certains formulaires
        initializeAjaxForms();
    }

    function initializeCalculations() {
        // Calcul automatique pour les factures
        const invoiceForms = document.querySelectorAll('#invoice-form');
        invoiceForms.forEach(form => {
            const subtotalInput = form.querySelector('#id_subtotal');
            const taxRateInput = form.querySelector('#id_tax_rate');
            const totalDisplay = form.querySelector('#total-display');

            if (subtotalInput && taxRateInput && totalDisplay) {
                function updateTotal() {
                    const subtotal = parseFloat(subtotalInput.value) || 0;
                    const taxRate = parseFloat(taxRateInput.value) || 0;
                    const taxAmount = (subtotal * taxRate) / 100;
                    const total = subtotal + taxAmount;

                    totalDisplay.textContent = total.toFixed(2) + ' €';
                }

                subtotalInput.addEventListener('input', updateTotal);
                taxRateInput.addEventListener('input', updateTotal);
                updateTotal(); // Calcul initial
            }
        });

        // Calcul automatique pour les bons de commande
        const orderForms = document.querySelectorAll('#purchase-order-form');
        orderForms.forEach(form => {
            const itemRows = form.querySelectorAll('.item-row');

            itemRows.forEach(row => {
                const quantityInput = row.querySelector('.quantity');
                const unitPriceInput = row.querySelector('.unit-price');
                const totalInput = row.querySelector('.total');

                if (quantityInput && unitPriceInput && totalInput) {
                    function updateRowTotal() {
                        const quantity = parseFloat(quantityInput.value) || 0;
                        const unitPrice = parseFloat(unitPriceInput.value) || 0;
                        const total = quantity * unitPrice;

                        totalInput.value = total.toFixed(2);
                        updateOrderTotal(form);
                    }

                    quantityInput.addEventListener('input', updateRowTotal);
                    unitPriceInput.addEventListener('input', updateRowTotal);
                }
            });
        });
    }

    function updateOrderTotal(form) {
        const totalInputs = form.querySelectorAll('.total');
        let orderTotal = 0;

        totalInputs.forEach(input => {
            orderTotal += parseFloat(input.value) || 0;
        });

        const orderTotalDisplay = form.querySelector('#order-total-display');
        if (orderTotalDisplay) {
            orderTotalDisplay.textContent = orderTotal.toFixed(2) + ' €';
        }

        const orderTotalInput = form.querySelector('#id_total_amount');
        if (orderTotalInput) {
            orderTotalInput.value = orderTotal.toFixed(2);
        }
    }

    function initializeValidation() {
        const forms = document.querySelectorAll('.form-intranet');

        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                }
            });
        });
    }

    function validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                showFieldError(field, 'Ce champ est obligatoire');
                isValid = false;
            } else {
                clearFieldError(field);
            }
        });

        // Validation spécifique pour les emails
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !isValidEmail(field.value)) {
                showFieldError(field, 'Adresse email invalide');
                isValid = false;
            }
        });

        return isValid;
    }

    function showFieldError(field, message) {
        clearFieldError(field);

        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: #ef4444;
            font-size: 12px;
            margin-top: 4px;
            font-weight: 500;
        `;

        field.parentNode.appendChild(errorDiv);
        field.style.borderColor = '#ef4444';
    }

    function clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.style.borderColor = '';
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function initializeAjaxForms() {
        const ajaxForms = document.querySelectorAll('[data-ajax-form]');

        ajaxForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(this);
                const url = this.action || window.location.href;

                fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showMessage('success', data.message || 'Opération réussie');
                        if (data.redirect) {
                            setTimeout(() => {
                                window.location.href = data.redirect;
                            }, 1000);
                        }
                    } else {
                        showMessage('error', data.message || 'Une erreur est survenue');
                    }
                })
                .catch(error => {
                    console.error('Erreur AJAX:', error);
                    showMessage('error', 'Erreur de communication');
                });
            });
        });
    }

    // ========== ANIMATIONS ==========

    function initializeAnimations() {
        // Animation des cartes au scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, observerOptions);

        const animateElements = document.querySelectorAll('.stat-card, .info-card, .table-intranet');
        animateElements.forEach(element => {
            observer.observe(element);
        });
    }

    // ========== UTILITAIRES ==========

    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    function showMessage(type, message) {
        // Créer une notification temporaire
        const notification = document.createElement('div');
        notification.className = `alert-intranet alert-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            animation: fadeInUp 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Supprimer après 5 secondes
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    // ========== EXPORTS ==========

    // Exposer certaines fonctions globalement si nécessaire
    window.IntranetUtils = {
        openModal,
        closeModal,
        showMessage
    };

    console.log('🚀 Intranet utilities loaded');
});
