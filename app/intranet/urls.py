from django.urls import path
from . import views

app_name = 'intranet'

urlpatterns = [
    # Page d'accueil
    path('', views.intranet_home, name='home'),

    # ========== FACTURES ==========
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),

    # ========== TRÉSORERIE ==========
    path('treasury/', views.treasury_list, name='treasury_list'),
    path('treasury/create/', views.treasury_create, name='treasury_create'),

    # ========== PIÈCES JOINTES ==========
    path('attachments/', views.attachment_list, name='attachment_list'),
    path('attachments/upload/', views.attachment_upload, name='attachment_upload'),

    # ========== BONS DE COMMANDE ==========
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
]
