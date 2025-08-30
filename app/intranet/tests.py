from django.test import TestCase
from django.contrib.auth.models import User
from .models import Invoice, Treasury, PurchaseOrder, Attachment


class IntranetTestCase(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )

    def test_invoice_creation(self):
        """Test de création d'une facture"""
        invoice = Invoice.objects.create(
            invoice_number='TEST-001',
            client_name='Client Test',
            client_address='123 Rue Test',
            client_email='client@test.com',
            subtotal=1000.00,
            tax_rate=20.00,
            status='draft',
            created_by=self.user
        )

        self.assertEqual(invoice.invoice_number, 'TEST-001')
        self.assertEqual(invoice.client_name, 'Client Test')
        self.assertEqual(invoice.total_amount, 1200.00)  # 1000 + 20% TVA

    def test_treasury_transaction(self):
        """Test de création d'une transaction trésorerie"""
        transaction = Treasury.objects.create(
            type='income',
            category='sales',
            description='Vente test',
            amount=500.00,
            created_by=self.user
        )

        self.assertEqual(transaction.type, 'income')
        self.assertEqual(transaction.amount, 500.00)
        self.assertEqual(transaction.created_by, self.user)

    def test_purchase_order_creation(self):
        """Test de création d'un bon de commande"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier_name='Fournisseur Test',
            supplier_address='456 Rue Fournisseur',
            supplier_email='fournisseur@test.com',
            total_amount=750.00,
            status='draft',
            created_by=self.user
        )

        self.assertEqual(order.order_number, 'PO-TEST-001')
        self.assertEqual(order.supplier_name, 'Fournisseur Test')
        self.assertEqual(order.total_amount, 750.00)
