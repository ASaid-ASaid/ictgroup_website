from django.contrib import admin
from .models import Invoice, InvoiceItem, Treasury, Attachment, PurchaseOrder, PurchaseOrderItem


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client_name', 'total_amount', 'status', 'issue_date', 'due_date', 'created_by']
    list_filter = ['status', 'issue_date', 'due_date', 'created_by']
    search_fields = ['invoice_number', 'client_name', 'client_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Informations générales', {
            'fields': ('invoice_number', 'client_name', 'client_address', 'client_email', 'client_phone')
        }),
        ('Dates et montants', {
            'fields': ('issue_date', 'due_date', 'subtotal', 'tax_rate', 'status')
        }),
        ('Informations système', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'quantity', 'unit_price', 'total', 'invoice']
    list_filter = ['invoice']
    search_fields = ['description', 'invoice__invoice_number']


@admin.register(Treasury)
class TreasuryAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'category', 'description', 'amount', 'created_by']
    list_filter = ['type', 'category', 'date', 'created_by']
    search_fields = ['description', 'reference']
    readonly_fields = ['created_at']
    ordering = ['-date']

    fieldsets = (
        ('Informations générales', {
            'fields': ('date', 'type', 'category', 'description', 'amount', 'reference')
        }),
        ('Virements', {
            'fields': ('from_account', 'to_account'),
            'classes': ('collapse',)
        }),
        ('Informations système', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'uploaded_by', 'uploaded_at', 'file']
    list_filter = ['file_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier_name', 'total_amount', 'status', 'order_date', 'created_by']
    list_filter = ['status', 'order_date', 'created_by']
    search_fields = ['order_number', 'supplier_name', 'supplier_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Informations générales', {
            'fields': ('order_number', 'supplier_name', 'supplier_address', 'supplier_email', 'supplier_phone')
        }),
        ('Dates et montants', {
            'fields': ('order_date', 'expected_delivery_date', 'actual_delivery_date', 'total_amount', 'status')
        }),
        ('Informations système', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'quantity', 'unit_price', 'total', 'purchase_order']
    list_filter = ['purchase_order']
    search_fields = ['description', 'purchase_order__order_number']
