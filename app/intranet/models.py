from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils import timezone
import os


class Invoice(models.Model):
    """Modèle pour les factures"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    client_name = models.CharField(max_length=200, verbose_name="Nom du client")
    client_address = models.TextField(verbose_name="Adresse du client")
    client_email = models.EmailField(verbose_name="Email du client")
    client_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone du client")

    issue_date = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    due_date = models.DateField(verbose_name="Date d'échéance")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sous-total HT")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00, verbose_name="Taux de TVA (%)")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant TVA")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total TTC")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-created_at']

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.client_name}"

    def save(self, *args, **kwargs):
        # Calcul automatique de la TVA et du total
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Lignes de facture"""
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, verbose_name="Description")
    quantity = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix unitaire HT")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total HT")

    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Treasury(models.Model):
    """Modèle pour la trésorerie"""
    TRANSACTION_TYPES = [
        ('income', 'Recette'),
        ('expense', 'Dépense'),
        ('transfer', 'Virement'),
    ]

    CATEGORY_CHOICES = [
        ('sales', 'Ventes'),
        ('services', 'Services'),
        ('supplies', 'Fournitures'),
        ('rent', 'Loyer'),
        ('utilities', 'Charges'),
        ('salary', 'Salaires'),
        ('taxes', 'Taxes'),
        ('other', 'Autre'),
    ]

    date = models.DateField(default=timezone.now, verbose_name="Date")
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Type")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Catégorie")
    description = models.CharField(max_length=200, verbose_name="Description")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")

    # Pour les virements
    from_account = models.CharField(max_length=100, blank=True, verbose_name="Compte source")
    to_account = models.CharField(max_length=100, blank=True, verbose_name="Compte destination")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction trésorerie"
        verbose_name_plural = "Transactions trésorerie"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.description} - {self.amount}€"


class Attachment(models.Model):
    """Modèle pour les pièces jointes"""
    FILE_TYPES = [
        ('invoice', 'Facture'),
        ('receipt', 'Reçu'),
        ('contract', 'Contrat'),
        ('quote', 'Devis'),
        ('other', 'Autre'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, verbose_name="Type de fichier")
    file = models.FileField(upload_to='intranet/attachments/%Y/%m/', verbose_name="Fichier")
    description = models.TextField(blank=True, verbose_name="Description")

    # Relations optionnelles
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Facture liée")
    purchase_order = models.ForeignKey('PurchaseOrder', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Bon de commande lié")

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Téléchargé par")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def filename(self):
        return os.path.basename(self.file.name)


class PurchaseOrder(models.Model):
    """Modèle pour les bons de commande"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyé'),
        ('approved', 'Approuvé'),
        ('received', 'Reçu'),
        ('cancelled', 'Annulé'),
    ]

    order_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de commande")
    supplier_name = models.CharField(max_length=200, verbose_name="Nom du fournisseur")
    supplier_address = models.TextField(verbose_name="Adresse du fournisseur")
    supplier_email = models.EmailField(verbose_name="Email du fournisseur")
    supplier_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone du fournisseur")

    order_date = models.DateField(default=timezone.now, verbose_name="Date de commande")
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name="Date de livraison prévue")
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name="Date de livraison effective")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ['-created_at']

    def __str__(self):
        return f"BC {self.order_number} - {self.supplier_name}"


class PurchaseOrderItem(models.Model):
    """Lignes de bon de commande"""
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, verbose_name="Description")
    quantity = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix unitaire")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    class Meta:
        verbose_name = "Ligne de bon de commande"
        verbose_name_plural = "Lignes de bon de commande"

    def __str__(self):
        return f"{self.description} - {self.purchase_order.order_number}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
