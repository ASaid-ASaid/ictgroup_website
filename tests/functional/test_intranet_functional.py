"""
Tests fonctionnels pour l'application Intranet ICTGROUP
Tests end-to-end des scénarios utilisateur complets
"""

from django.test import TestCase, LiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from decimal import Decimal
import time

from intranet.models import Invoice, Treasury, PurchaseOrder, Attachment


class InvoiceFunctionalTest(TestCase):
    """Tests fonctionnels pour le workflow facturation"""

    def setUp(self):
        """Configuration pour les tests fonctionnels"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@ictgroup.com',
            password='admin123',
            is_superuser=True
        )

        # Créer des données de test
        self.test_invoice = Invoice.objects.create(
            invoice_number='FUNC-TEST-001',
            client_name='Client Fonctionnel Test',
            client_address='123 Rue Fonctionnel\n75001 Paris',
            client_email='fonctionnel@test.com',
            client_phone='+33123456789',
            subtotal=Decimal('2500.00'),
            tax_rate=Decimal('20.00'),
            status='draft',
            notes='Test fonctionnel facture',
            created_by=self.admin_user
        )

    def test_invoice_creation_workflow(self):
        """Test du workflow complet de création de facture"""
        # 1. Création de la facture
        invoice_data = {
            'invoice_number': 'FUNC-WORKFLOW-001',
            'client_name': 'Client Workflow Fonctionnel',
            'client_address': '456 Rue Workflow',
            'client_email': 'workflow@fonctionnel.com',
            'client_phone': '+33456789012',
            'issue_date': '2025-08-20',
            'due_date': '2025-09-20',
            'subtotal': '5000.00',
            'tax_rate': '20.00',
            'status': 'draft',
            'notes': 'Test workflow fonctionnel'
        }

        # Simuler la création via formulaire
        from intranet.forms import InvoiceForm
        form = InvoiceForm(data=invoice_data)
        self.assertTrue(form.is_valid())

        invoice = form.save(commit=False)
        invoice.created_by = self.admin_user
        invoice.save()

        # 2. Vérifications des calculs
        self.assertEqual(invoice.total_amount, Decimal('6000.00'))  # 5000 + 1000 TVA
        self.assertEqual(invoice.tax_amount, Decimal('1000.00'))   # 5000 * 20%

        # 3. Test de modification de statut
        invoice.status = 'sent'
        invoice.save()
        self.assertEqual(invoice.status, 'sent')

        # 4. Test de passage en payé
        invoice.status = 'paid'
        invoice.save()
        self.assertEqual(invoice.status, 'paid')

    def test_invoice_search_and_filter(self):
        """Test des fonctionnalités de recherche et filtrage"""
        # Créer plusieurs factures pour les tests
        invoices_data = [
            {
                'invoice_number': 'SEARCH-001',
                'client_name': 'Client Alpha',
                'client_email': 'alpha@test.com',
                'subtotal': Decimal('1000.00'),
                'status': 'paid'
            },
            {
                'invoice_number': 'SEARCH-002',
                'client_name': 'Client Beta SARL',
                'client_email': 'beta@test.com',
                'subtotal': Decimal('2000.00'),
                'status': 'sent'
            },
            {
                'invoice_number': 'SEARCH-003',
                'client_name': 'Client Gamma',
                'client_email': 'gamma@test.com',
                'subtotal': Decimal('1500.00'),
                'status': 'overdue'
            }
        ]

        for data in invoices_data:
            Invoice.objects.create(
                client_address='123 Rue Test',
                client_phone='+33123456789',
                tax_rate=Decimal('20.00'),
                created_by=self.admin_user,
                **data
            )

        # Test de recherche par numéro
        search_results = Invoice.objects.filter(invoice_number__icontains='SEARCH-001')
        self.assertEqual(search_results.count(), 1)

        # Test de recherche par client
        client_results = Invoice.objects.filter(client_name__icontains='Beta')
        self.assertEqual(client_results.count(), 1)

        # Test de filtrage par statut
        paid_invoices = Invoice.objects.filter(status='paid')
        self.assertEqual(paid_invoices.count(), 1)

        sent_invoices = Invoice.objects.filter(status='sent')
        self.assertEqual(sent_invoices.count(), 1)

    def test_invoice_reporting(self):
        """Test des fonctionnalités de reporting"""
        # Créer des factures avec différentes dates et statuts
        from datetime import date, timedelta

        base_date = date.today()

        # Facture du mois en cours - payée
        Invoice.objects.create(
            invoice_number='REPORT-001',
            client_name='Client Report 1',
            client_address='123 Rue Report',
            client_email='report1@test.com',
            issue_date=base_date,
            subtotal=Decimal('3000.00'),
            tax_rate=Decimal('20.00'),
            status='paid',
            created_by=self.admin_user
        )

        # Facture du mois dernier - payée
        Invoice.objects.create(
            invoice_number='REPORT-002',
            client_name='Client Report 2',
            client_address='456 Rue Report',
            client_email='report2@test.com',
            issue_date=base_date - timedelta(days=30),
            subtotal=Decimal('4000.00'),
            tax_rate=Decimal('20.00'),
            status='paid',
            created_by=self.admin_user
        )

        # Facture en attente
        Invoice.objects.create(
            invoice_number='REPORT-003',
            client_name='Client Report 3',
            client_address='789 Rue Report',
            client_email='report3@test.com',
            issue_date=base_date,
            subtotal=Decimal('2000.00'),
            tax_rate=Decimal('20.00'),
            status='sent',
            created_by=self.admin_user
        )

        # Calculs de reporting
        total_revenue = Invoice.objects.filter(status='paid').aggregate(
            total=Decimal('0.00') + sum(Decimal(str(inv.total_amount)) for inv in Invoice.objects.filter(status='paid'))
        )['total'] or Decimal('0.00')

        pending_amount = Invoice.objects.filter(status__in=['sent', 'overdue']).aggregate(
            total=Decimal('0.00') + sum(Decimal(str(inv.total_amount)) for inv in Invoice.objects.filter(status__in=['sent', 'overdue']))
        )['total'] or Decimal('0.00')

        # Vérifications
        self.assertEqual(total_revenue, Decimal('8400.00'))  # (3000+600) + (4000+800) = 3600 + 4800
        self.assertEqual(pending_amount, Decimal('2400.00')) # 2000 + 400 TVA


class TreasuryFunctionalTest(TestCase):
    """Tests fonctionnels pour la gestion de trésorerie"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@ictgroup.com',
            password='admin123',
            is_superuser=True
        )

    def test_treasury_workflow(self):
        """Test du workflow trésorerie complet"""
        # 1. Enregistrer des recettes
        incomes = [
            {'description': 'Vente produit A', 'amount': '5000.00'},
            {'description': 'Prestation service B', 'amount': '3000.00'},
            {'description': 'Vente produit C', 'amount': '1500.00'},
        ]

        for income in incomes:
            Treasury.objects.create(
                type='income',
                category='sales',
                description=income['description'],
                amount=Decimal(income['amount']),
                created_by=self.admin_user
            )

        # 2. Enregistrer des dépenses
        expenses = [
            {'description': 'Loyer bureau', 'amount': '2000.00', 'category': 'rent'},
            {'description': 'Achat fournitures', 'amount': '800.00', 'category': 'supplies'},
            {'description': 'Facture électricité', 'amount': '300.00', 'category': 'utilities'},
            {'description': 'Salaires équipe', 'amount': '5000.00', 'category': 'salary'},
        ]

        for expense in expenses:
            Treasury.objects.create(
                type='expense',
                category=expense['category'],
                description=expense['description'],
                amount=Decimal(expense['amount']),
                created_by=self.admin_user
            )

        # 3. Calculer les totaux
        total_income = sum(Decimal(str(t.amount)) for t in Treasury.objects.filter(type='income'))
        total_expenses = sum(Decimal(str(t.amount)) for t in Treasury.objects.filter(type='expense'))
        net_result = total_income - total_expenses

        # Vérifications
        self.assertEqual(total_income, Decimal('9500.00'))   # 5000 + 3000 + 1500
        self.assertEqual(total_expenses, Decimal('8100.00')) # 2000 + 800 + 300 + 5000
        self.assertEqual(net_result, Decimal('1400.00'))     # 9500 - 8100

    def test_category_analysis(self):
        """Test de l'analyse par catégories"""
        # Créer des transactions dans différentes catégories
        transactions = [
            {'type': 'income', 'category': 'sales', 'amount': '3000.00'},
            {'type': 'income', 'category': 'services', 'amount': '2000.00'},
            {'type': 'expense', 'category': 'rent', 'amount': '1500.00'},
            {'type': 'expense', 'category': 'supplies', 'amount': '500.00'},
            {'type': 'expense', 'category': 'utilities', 'amount': '300.00'},
        ]

        for trans in transactions:
            Treasury.objects.create(
                type=trans['type'],
                category=trans['category'],
                description=f'Test {trans["category"]}',
                amount=Decimal(trans['amount']),
                created_by=self.admin_user
            )

        # Analyse par catégorie
        sales_total = sum(Decimal(str(t.amount)) for t in Treasury.objects.filter(category='sales'))
        services_total = sum(Decimal(str(t.amount)) for t in Treasury.objects.filter(category='services'))
        rent_total = sum(Decimal(str(t.amount)) for t in Treasury.objects.filter(category='rent'))

        self.assertEqual(sales_total, Decimal('3000.00'))
        self.assertEqual(services_total, Decimal('2000.00'))
        self.assertEqual(rent_total, Decimal('1500.00'))


class PurchaseOrderFunctionalTest(TestCase):
    """Tests fonctionnels pour les bons de commande"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@ictgroup.com',
            password='admin123',
            is_superuser=True
        )

    def test_purchase_order_lifecycle(self):
        """Test du cycle de vie complet d'un bon de commande"""
        from datetime import date, timedelta

        # 1. Création du bon de commande
        order = PurchaseOrder.objects.create(
            order_number='PO-FUNC-001',
            supplier_name='Fournisseur Fonctionnel SARL',
            supplier_address='123 Rue Fournisseur\n69000 Lyon',
            supplier_email='contact@fournisseur-fonctionnel.com',
            supplier_phone='+33456789012',
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=15),
            total_amount=Decimal('3500.00'),
            status='draft',
            notes='Test fonctionnel bon de commande',
            created_by=self.admin_user
        )

        # 2. Passage en statut "envoyé"
        order.status = 'sent'
        order.save()
        self.assertEqual(order.status, 'sent')

        # 3. Approbation
        order.status = 'approved'
        order.save()
        self.assertEqual(order.status, 'approved')

        # 4. Réception avec date effective
        delivery_date = date.today() + timedelta(days=12)
        order.status = 'received'
        order.actual_delivery_date = delivery_date
        order.save()

        self.assertEqual(order.status, 'received')
        self.assertEqual(order.actual_delivery_date, delivery_date)

        # 5. Calcul du délai de livraison
        if order.actual_delivery_date and order.expected_delivery_date:
            delay_days = (order.actual_delivery_date - order.expected_delivery_date).days
            self.assertEqual(delay_days, -3)  # Livraison 3 jours en avance

    def test_supplier_management(self):
        """Test de la gestion des fournisseurs"""
        suppliers_data = [
            {
                'name': 'Tech Solutions SARL',
                'email': 'contact@techsolutions.com',
                'phone': '+33123456789'
            },
            {
                'name': 'Office Plus',
                'email': 'commandes@officeplus.fr',
                'phone': '+33456789012'
            },
            {
                'name': 'Impression Express',
                'email': 'contact@impressionexpress.com',
                'phone': '+33567890123'
            }
        ]

        # Créer des bons de commande pour différents fournisseurs
        for i, supplier in enumerate(suppliers_data, 1):
            PurchaseOrder.objects.create(
                order_number=f'PO-SUPPLIER-{i:03d}',
                supplier_name=supplier['name'],
                supplier_address=f'{123 + i} Rue Test',
                supplier_email=supplier['email'],
                supplier_phone=supplier['phone'],
                total_amount=Decimal('1000.00') * i,
                status='draft',
                created_by=self.admin_user
            )

        # Vérifications
        total_orders = PurchaseOrder.objects.count()
        self.assertEqual(total_orders, 3)

        # Recherche par fournisseur
        tech_orders = PurchaseOrder.objects.filter(supplier_name__icontains='Tech')
        self.assertEqual(tech_orders.count(), 1)

        office_orders = PurchaseOrder.objects.filter(supplier_email__icontains='officeplus')
        self.assertEqual(office_orders.count(), 1)


class DocumentManagementFunctionalTest(TestCase):
    """Tests fonctionnels pour la gestion documentaire"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@ictgroup.com',
            password='admin123',
            is_superuser=True
        )

        # Créer une facture pour les tests d'association
        self.test_invoice = Invoice.objects.create(
            invoice_number='DOC-TEST-001',
            client_name='Client Document Test',
            client_address='123 Rue Document',
            client_email='doc@test.com',
            subtotal=Decimal('2000.00'),
            tax_rate=Decimal('20.00'),
            status='draft',
            created_by=self.admin_user
        )

    def test_document_association_workflow(self):
        """Test du workflow d'association documents-factures"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        # 1. Upload d'une facture PDF
        invoice_file = SimpleUploadedFile(
            "facture_001.pdf",
            b"Contenu PDF de la facture",
            content_type="application/pdf"
        )

        invoice_attachment = Attachment.objects.create(
            title='Facture PDF DOC-TEST-001',
            file_type='invoice',
            file=invoice_file,
            description='Facture au format PDF',
            invoice=self.test_invoice,
            uploaded_by=self.admin_user
        )

        # 2. Upload d'un reçu de paiement
        receipt_file = SimpleUploadedFile(
            "recu_paiement_001.pdf",
            b"Contenu du reçu de paiement",
            content_type="application/pdf"
        )

        receipt_attachment = Attachment.objects.create(
            title='Reçu paiement DOC-TEST-001',
            file_type='receipt',
            file=receipt_file,
            description='Reçu de paiement facture DOC-TEST-001',
            invoice=self.test_invoice,
            uploaded_by=self.admin_user
        )

        # 3. Upload d'un contrat séparé (non lié)
        contract_file = SimpleUploadedFile(
            "contrat_service.pdf",
            b"Contenu du contrat de service",
            content_type="application/pdf"
        )

        contract_attachment = Attachment.objects.create(
            title='Contrat de service annuel',
            file_type='contract',
            file=contract_file,
            description='Contrat de service 2025',
            uploaded_by=self.admin_user
        )

        # Vérifications
        # Documents liés à la facture
        invoice_docs = Attachment.objects.filter(invoice=self.test_invoice)
        self.assertEqual(invoice_docs.count(), 2)

        # Tous les documents
        all_docs = Attachment.objects.all()
        self.assertEqual(all_docs.count(), 3)

        # Documents par type
        pdf_docs = Attachment.objects.filter(file__endswith='.pdf')
        self.assertEqual(pdf_docs.count(), 3)

        contract_docs = Attachment.objects.filter(file_type='contract')
        self.assertEqual(contract_docs.count(), 1)

    def test_document_search_and_filter(self):
        """Test de recherche et filtrage des documents"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Créer différents types de documents
        documents_data = [
            {
                'title': 'Facture Client Alpha',
                'file_type': 'invoice',
                'filename': 'facture_alpha.pdf',
                'content': b'Facture Alpha'
            },
            {
                'title': 'Devis Projet Beta',
                'file_type': 'quote',
                'filename': 'devis_beta.pdf',
                'content': b'Devis Beta'
            },
            {
                'title': 'Contrat Service Gamma',
                'file_type': 'contract',
                'filename': 'contrat_gamma.pdf',
                'content': b'Contrat Gamma'
            },
            {
                'title': 'Reçu Fournisseur Delta',
                'file_type': 'receipt',
                'filename': 'recu_delta.pdf',
                'content': b'Reçu Delta'
            }
        ]

        for doc_data in documents_data:
            file_obj = SimpleUploadedFile(
                doc_data['filename'],
                doc_data['content'],
                content_type="application/pdf"
            )

            Attachment.objects.create(
                title=doc_data['title'],
                file_type=doc_data['file_type'],
                file=file_obj,
                description=f'Document de test: {doc_data["title"]}',
                uploaded_by=self.admin_user
            )

        # Tests de recherche
        # Par titre
        alpha_docs = Attachment.objects.filter(title__icontains='Alpha')
        self.assertEqual(alpha_docs.count(), 1)

        # Par type
        invoice_docs = Attachment.objects.filter(file_type='invoice')
        self.assertEqual(invoice_docs.count(), 1)

        contract_docs = Attachment.objects.filter(file_type='contract')
        self.assertEqual(contract_docs.count(), 1)

        # Recherche multiple
        devis_quote_docs = Attachment.objects.filter(
            file_type__in=['quote', 'contract']
        )
        self.assertEqual(devis_quote_docs.count(), 2)


# Tests Selenium pour l'interface utilisateur (commentés pour éviter les dépendances)
"""
class IntranetUITest(LiveServerTestCase):
    '''Tests d'interface utilisateur avec Selenium'''

    def setUp(self):
        # Configuration Selenium (nécessite ChromeDriver)
        options = Options()
        options.add_argument('--headless')  # Mode headless pour CI
        self.selenium = webdriver.Chrome(options=options)

        # Créer utilisateur admin
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@ictgroup.com',
            password='admin123',
            is_superuser=True
        )

    def tearDown(self):
        self.selenium.quit()

    def test_intranet_login_and_navigation(self):
        '''Test de connexion et navigation dans l'intranet'''
        # Ouvrir la page de connexion
        self.selenium.get(f'{self.live_server_url}/admin/login/')

        # Se connecter
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]')

        username_input.send_keys('admin')
        password_input.send_keys('admin123')
        submit_button.click()

        # Attendre la redirection
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/admin/')
        )

        # Naviguer vers l'intranet
        self.selenium.get(f'{self.live_server_url}/intranet/')

        # Vérifier que nous sommes sur la page intranet
        self.assertIn('Intranet', self.selenium.title)

        # Vérifier la présence d'éléments clés
        dashboard_elements = self.selenium.find_elements(By.CLASS_NAME, 'dashboard-card')
        self.assertGreater(len(dashboard_elements), 0)
"""
