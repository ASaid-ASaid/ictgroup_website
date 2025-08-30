"""
Tests unitaires pour l'application Intranet ICTGROUP
Tests des modèles, formulaires et fonctionnalités de base
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from decimal import Decimal
import os

from intranet.models import (
    Invoice, InvoiceItem, Treasury, PurchaseOrder,
    PurchaseOrderItem, Attachment
)
from intranet.forms import InvoiceForm, TreasuryForm, PurchaseOrderForm


class InvoiceModelTest(TestCase):
    """Tests pour le modèle Invoice"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_invoice_creation(self):
        """Test de création d'une facture avec calculs automatiques"""
        invoice = Invoice.objects.create(
            invoice_number='TEST-001',
            client_name='Client Test SA',
            client_address='123 Rue Test\n75001 Paris',
            client_email='contact@clienttest.com',
            client_phone='+33123456789',
            subtotal=Decimal('1000.00'),
            tax_rate=Decimal('20.00'),
            status='draft',
            created_by=self.user
        )

        # Vérifications des données
        self.assertEqual(invoice.invoice_number, 'TEST-001')
        self.assertEqual(invoice.client_name, 'Client Test SA')
        self.assertEqual(invoice.subtotal, Decimal('1000.00'))
        self.assertEqual(invoice.tax_rate, Decimal('20.00'))

        # Vérifications des calculs automatiques
        self.assertEqual(invoice.tax_amount, Decimal('200.00'))  # 1000 * 20%
        self.assertEqual(invoice.total_amount, Decimal('1200.00'))  # 1000 + 200

    def test_invoice_status_choices(self):
        """Test des choix de statut valides"""
        valid_statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']

        for status in valid_statuses:
            invoice = Invoice.objects.create(
                invoice_number=f'TEST-{status.upper()}',
                client_name='Client Test',
                client_address='123 Rue Test',
                client_email='test@test.com',
                subtotal=Decimal('100.00'),
                tax_rate=Decimal('20.00'),
                status=status,
                created_by=self.user
            )
            self.assertEqual(invoice.status, status)

    def test_invoice_str_representation(self):
        """Test de la représentation string de la facture"""
        invoice = Invoice.objects.create(
            invoice_number='TEST-001',
            client_name='Client Test SA',
            client_address='123 Rue Test',
            client_email='test@test.com',
            subtotal=Decimal('100.00'),
            tax_rate=Decimal('20.00'),
            status='draft',
            created_by=self.user
        )

        expected_str = "Facture TEST-001 - Client Test SA"
        self.assertEqual(str(invoice), expected_str)


class InvoiceItemModelTest(TestCase):
    """Tests pour le modèle InvoiceItem"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

        self.invoice = Invoice.objects.create(
            invoice_number='TEST-001',
            client_name='Client Test',
            client_address='123 Rue Test',
            client_email='test@test.com',
            subtotal=Decimal('100.00'),
            tax_rate=Decimal('20.00'),
            status='draft',
            created_by=self.user
        )

    def test_invoice_item_creation(self):
        """Test de création d'une ligne de facture"""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description='Service de développement',
            quantity=Decimal('10.00'),
            unit_price=Decimal('50.00')
        )

        # Vérifications des calculs
        self.assertEqual(item.total, Decimal('500.00'))  # 10 * 50
        self.assertEqual(item.description, 'Service de développement')

    def test_invoice_item_str_representation(self):
        """Test de la représentation string d'une ligne"""
        item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description='Service test',
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00')
        )

        expected_str = "Service test - TEST-001"
        self.assertEqual(str(item), expected_str)


class TreasuryModelTest(TestCase):
    """Tests pour le modèle Treasury"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_income_transaction(self):
        """Test de création d'une transaction recette"""
        transaction = Treasury.objects.create(
            type='income',
            category='sales',
            description='Vente produit',
            amount=Decimal('1500.00'),
            created_by=self.user
        )

        self.assertEqual(transaction.type, 'income')
        self.assertEqual(transaction.category, 'sales')
        self.assertEqual(transaction.amount, Decimal('1500.00'))

    def test_expense_transaction(self):
        """Test de création d'une transaction dépense"""
        transaction = Treasury.objects.create(
            type='expense',
            category='supplies',
            description='Achat fournitures',
            amount=Decimal('300.00'),
            created_by=self.user
        )

        self.assertEqual(transaction.type, 'expense')
        self.assertEqual(transaction.category, 'supplies')
        self.assertEqual(transaction.amount, Decimal('300.00'))

    def test_transfer_transaction(self):
        """Test de création d'un virement"""
        transaction = Treasury.objects.create(
            type='transfer',
            category='other',
            description='Virement compte épargne',
            amount=Decimal('5000.00'),
            from_account='Compte courant',
            to_account='Livret A',
            created_by=self.user
        )

        self.assertEqual(transaction.type, 'transfer')
        self.assertEqual(transaction.from_account, 'Compte courant')
        self.assertEqual(transaction.to_account, 'Livret A')


class PurchaseOrderModelTest(TestCase):
    """Tests pour le modèle PurchaseOrder"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_purchase_order_creation(self):
        """Test de création d'un bon de commande"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier_name='Fournisseur Test SARL',
            supplier_address='456 Rue Fournisseur\n69000 Lyon',
            supplier_email='contact@fournisseur.com',
            supplier_phone='+33456789012',
            total_amount=Decimal('2500.00'),
            status='draft',
            created_by=self.user
        )

        self.assertEqual(order.order_number, 'PO-TEST-001')
        self.assertEqual(order.supplier_name, 'Fournisseur Test SARL')
        self.assertEqual(order.total_amount, Decimal('2500.00'))
        self.assertEqual(order.status, 'draft')

    def test_purchase_order_str_representation(self):
        """Test de la représentation string du bon de commande"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier_name='Fournisseur Test',
            supplier_address='456 Rue Test',
            supplier_email='test@test.com',
            total_amount=Decimal('1000.00'),
            status='draft',
            created_by=self.user
        )

        expected_str = "BC PO-TEST-001 - Fournisseur Test"
        self.assertEqual(str(order), expected_str)


class AttachmentModelTest(TestCase):
    """Tests pour le modèle Attachment"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_attachment_creation(self):
        """Test de création d'une pièce jointe"""
        # Créer un fichier de test
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"contenu du fichier test",
            content_type="application/pdf"
        )

        attachment = Attachment.objects.create(
            title='Document test',
            file_type='contract',
            file=test_file,
            description='Document de test pour les tests unitaires',
            uploaded_by=self.user
        )

        self.assertEqual(attachment.title, 'Document test')
        self.assertEqual(attachment.file_type, 'contract')
        self.assertEqual(attachment.uploaded_by, self.user)
        self.assertIsNotNone(attachment.uploaded_at)

    def test_attachment_str_representation(self):
        """Test de la représentation string de la pièce jointe"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"contenu test",
            content_type="application/pdf"
        )

        attachment = Attachment.objects.create(
            title='Test Document',
            file_type='other',
            file=test_file,
            uploaded_by=self.user
        )

        self.assertEqual(str(attachment), 'Test Document')


class InvoiceFormTest(TestCase):
    """Tests pour le formulaire InvoiceForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_valid_invoice_form(self):
        """Test de formulaire valide"""
        form_data = {
            'invoice_number': 'FORM-TEST-001',
            'client_name': 'Client Formulaire',
            'client_address': '123 Rue Formulaire',
            'client_email': 'form@test.com',
            'client_phone': '+33123456789',
            'issue_date': '2025-08-15',
            'due_date': '2025-09-15',
            'subtotal': '2000.00',
            'tax_rate': '20.00',
            'status': 'draft',
            'notes': 'Test de formulaire'
        }

        form = InvoiceForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Sauvegarder et vérifier
        invoice = form.save(commit=False)
        invoice.created_by = self.user
        invoice.save()

        self.assertEqual(invoice.invoice_number, 'FORM-TEST-001')
        self.assertEqual(invoice.total_amount, Decimal('2400.00'))  # 2000 + 400 TVA

    def test_invalid_invoice_form(self):
        """Test de formulaire invalide"""
        form_data = {
            'invoice_number': '',  # Numéro requis manquant
            'client_name': '',     # Nom requis manquant
            'client_email': 'invalid-email',  # Email invalide
            'subtotal': '-100',    # Montant négatif invalide
        }

        form = InvoiceForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Vérifier les erreurs
        self.assertIn('invoice_number', form.errors)
        self.assertIn('client_name', form.errors)
        self.assertIn('client_email', form.errors)


class TreasuryFormTest(TestCase):
    """Tests pour le formulaire TreasuryForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_valid_treasury_form(self):
        """Test de formulaire trésorerie valide"""
        form_data = {
            'date': '2025-08-15',
            'type': 'income',
            'category': 'sales',
            'description': 'Vente test formulaire',
            'amount': '750.50',
            'reference': 'REF-TEST-001'
        }

        form = TreasuryForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Sauvegarder et vérifier
        transaction = form.save(commit=False)
        transaction.created_by = self.user
        transaction.save()

        self.assertEqual(transaction.type, 'income')
        self.assertEqual(transaction.amount, Decimal('750.50'))
        self.assertEqual(transaction.reference, 'REF-TEST-001')


class PurchaseOrderFormTest(TestCase):
    """Tests pour le formulaire PurchaseOrderForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_valid_purchase_order_form(self):
        """Test de formulaire bon de commande valide"""
        form_data = {
            'order_number': 'PO-FORM-TEST-001',
            'supplier_name': 'Fournisseur Formulaire',
            'supplier_address': '456 Rue Fournisseur',
            'supplier_email': 'supplier@test.com',
            'supplier_phone': '+33456789012',
            'order_date': '2025-08-15',
            'expected_delivery_date': '2025-08-30',
            'total_amount': '3200.00',
            'status': 'draft',
            'notes': 'Test formulaire bon de commande'
        }

        form = PurchaseOrderForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Sauvegarder et vérifier
        order = form.save(commit=False)
        order.created_by = self.user
        order.save()

        self.assertEqual(order.order_number, 'PO-FORM-TEST-001')
        self.assertEqual(order.supplier_name, 'Fournisseur Formulaire')
        self.assertEqual(order.total_amount, Decimal('3200.00'))
