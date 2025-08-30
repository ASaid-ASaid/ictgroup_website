from django import forms
from .models import Invoice, InvoiceItem, Treasury, Attachment, PurchaseOrder, PurchaseOrderItem


class InvoiceForm(forms.ModelForm):
    """Formulaire pour les factures"""

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'client_name', 'client_address', 'client_email',
            'client_phone', 'issue_date', 'due_date', 'subtotal', 'tax_rate',
            'status', 'notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'client_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class InvoiceItemForm(forms.ModelForm):
    """Formulaire pour les lignes de facture"""

    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Description de l\'article'}),
        }


class TreasuryForm(forms.ModelForm):
    """Formulaire pour les transactions trésorerie"""

    class Meta:
        model = Treasury
        fields = [
            'date', 'type', 'category', 'description', 'amount',
            'reference', 'from_account', 'to_account'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'Description de la transaction'}),
            'reference': forms.TextInput(attrs={'placeholder': 'Numéro de chèque, référence, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer les champs de virement si ce n'est pas un virement
        if self.instance and self.instance.type != 'transfer':
            self.fields['from_account'].widget = forms.HiddenInput()
            self.fields['to_account'].widget = forms.HiddenInput()


class AttachmentForm(forms.ModelForm):
    """Formulaire pour les pièces jointes"""

    class Meta:
        model = Attachment
        fields = ['title', 'file_type', 'file', 'description', 'invoice', 'purchase_order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PurchaseOrderForm(forms.ModelForm):
    """Formulaire pour les bons de commande"""

    class Meta:
        model = PurchaseOrder
        fields = [
            'order_number', 'supplier_name', 'supplier_address', 'supplier_email',
            'supplier_phone', 'order_date', 'expected_delivery_date', 'total_amount',
            'status', 'notes'
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'supplier_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    """Formulaire pour les lignes de bon de commande"""

    class Meta:
        model = PurchaseOrderItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Description de l\'article'}),
        }
