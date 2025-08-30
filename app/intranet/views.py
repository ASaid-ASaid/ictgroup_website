from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Invoice, Treasury, Attachment, PurchaseOrder
from .forms import InvoiceForm, TreasuryForm, AttachmentForm, PurchaseOrderForm
import json


def is_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')


@login_required
@user_passes_test(is_admin)
def intranet_home(request):
    """Page d'accueil de l'intranet"""
    # Statistiques générales
    total_invoices = Invoice.objects.count()
    total_invoices_amount = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_invoices = Invoice.objects.filter(status__in=['sent', 'overdue']).count()

    total_purchase_orders = PurchaseOrder.objects.count()
    pending_orders = PurchaseOrder.objects.filter(status__in=['sent', 'approved']).count()

    # Transactions récentes
    recent_transactions = Treasury.objects.select_related('created_by')[:5]

    # Factures récentes
    recent_invoices = Invoice.objects.select_related('created_by')[:5]

    context = {
        'total_invoices': total_invoices,
        'total_invoices_amount': total_invoices_amount,
        'pending_invoices': pending_invoices,
        'total_purchase_orders': total_purchase_orders,
        'pending_orders': pending_orders,
        'recent_transactions': recent_transactions,
        'recent_invoices': recent_invoices,
    }

    return render(request, 'intranet/home.html', context)


# ========== GESTION DES FACTURES ==========

@login_required
@user_passes_test(is_admin)
def invoice_list(request):
    """Liste des factures"""
    invoices = Invoice.objects.select_related('created_by').order_by('-created_at')

    # Filtres
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)

    # Recherche
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(client_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
    }

    return render(request, 'intranet/invoices/list.html', context)


@login_required
@user_passes_test(is_admin)
def invoice_create(request):
    """Créer une nouvelle facture"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('intranet:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()

    return render(request, 'intranet/invoices/create.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def invoice_detail(request, pk):
    """Détail d'une facture"""
    invoice = get_object_or_404(Invoice, pk=pk)

    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
    }

    return render(request, 'intranet/invoices/detail.html', context)


# ========== GESTION DE LA TRÉSORERIE ==========

@login_required
@user_passes_test(is_admin)
def treasury_list(request):
    """Liste des transactions trésorerie"""
    transactions = Treasury.objects.select_related('created_by').order_by('-date', '-created_at')

    # Filtres
    type_filter = request.GET.get('type')
    category_filter = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if type_filter:
        transactions = transactions.filter(type=type_filter)
    if category_filter:
        transactions = transactions.filter(category=category_filter)
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    # Calculs
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'type_filter': type_filter,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'intranet/treasury/list.html', context)


@login_required
@user_passes_test(is_admin)
def treasury_create(request):
    """Créer une nouvelle transaction"""
    if request.method == 'POST':
        form = TreasuryForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Transaction créée avec succès.')
            return redirect('intranet:treasury_list')
    else:
        form = TreasuryForm()

    return render(request, 'intranet/treasury/create.html', {'form': form})


# ========== GESTION DES PIÈCES JOINTES ==========

@login_required
@user_passes_test(is_admin)
def attachment_list(request):
    """Liste des pièces jointes"""
    attachments = Attachment.objects.select_related('uploaded_by', 'invoice', 'purchase_order').order_by('-uploaded_at')

    # Filtres
    file_type_filter = request.GET.get('file_type')
    if file_type_filter:
        attachments = attachments.filter(file_type=file_type_filter)

    # Pagination
    paginator = Paginator(attachments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'file_type_filter': file_type_filter,
    }

    return render(request, 'intranet/attachments/list.html', context)


@login_required
@user_passes_test(is_admin)
def attachment_upload(request):
    """Télécharger une pièce jointe"""
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Pièce jointe téléchargée avec succès.')
            return redirect('intranet:attachment_list')
    else:
        form = AttachmentForm()

    return render(request, 'intranet/attachments/upload.html', {'form': form})


# ========== GESTION DES BONS DE COMMANDE ==========

@login_required
@user_passes_test(is_admin)
def purchase_order_list(request):
    """Liste des bons de commande"""
    orders = PurchaseOrder.objects.select_related('created_by').order_by('-created_at')

    # Filtres
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Recherche
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(supplier_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
    }

    return render(request, 'intranet/purchase_orders/list.html', context)


@login_required
@user_passes_test(is_admin)
def purchase_order_create(request):
    """Créer un nouveau bon de commande"""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            messages.success(request, f'Bon de commande {order.order_number} créé avec succès.')
            return redirect('intranet:purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()

    return render(request, 'intranet/purchase_orders/create.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def purchase_order_detail(request, pk):
    """Détail d'un bon de commande"""
    order = get_object_or_404(PurchaseOrder, pk=pk)

    context = {
        'order': order,
        'items': order.items.all(),
    }

    return render(request, 'intranet/purchase_orders/detail.html', context)
